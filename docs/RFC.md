# RFC: Sistema de Webhooks de Notificação de Pedidos

| Campo | Valor |
| --- | --- |
| **Autor** | Larissa (Tech Lead) |
| **Status** | Em revisão |
| **Data** | 2026-07-26 |
| **Revisores** | Marcos (Product Manager), Bruno (Engenheiro Pleno, time de Pedidos), Diego (Engenheiro Sênior, time de Plataforma), Sofia (Engenheira de Segurança) |

## Resumo executivo (TL;DR)

Propomos notificar clientes B2B por webhook a cada mudança de status de pedido, usando o **padrão Outbox
no MySQL** já existente: o evento é gravado na mesma transação que altera o pedido, e um **worker em
processo separado** faz polling a cada 2 segundos para entregar via HTTP. Falhas entram em **retry com
backoff exponencial** (cinco tentativas, de 1 minuto a 12 horas) e, esgotadas as tentativas, o evento vai
para uma **dead letter queue** com replay manual restrito a ADMIN. Cada requisição é assinada em
**HMAC-SHA256** com secret única por endpoint, rotacionável com grace period de 24 horas. A entrega é
**at-least-once**, com `X-Event-Id` para deduplicação no cliente. Nenhuma infraestrutura nova é
introduzida — a feature é um módulo como os demais, reaproveitando os padrões do projeto.

## Contexto e problema

Três clientes B2B — Atlas Comercial, MaxDistribuição e Nova Cargo — pediram formalmente para serem
notificados quando o status dos pedidos deles muda. Hoje eles fazem polling em `GET /orders` de tempos
em tempos, o que torna a integração lenta e cara do lado deles. A Atlas sinalizou possibilidade de
migrar para um concorrente se a entrega não sair até o fim do trimestre.

O OMS não tem nenhum mecanismo de notificação externa, eventos, filas ou webhooks. O ciclo de vida do
pedido é controlado por máquina de estados, com controle transacional de estoque e auditoria de mudanças
de status — mas nada disso escapa dos limites do sistema.

Do ponto de vista do cliente, "tempo real" significa qualquer latência abaixo de 10 segundos. O escopo é
exclusivamente **outbound**: a plataforma envia, os clientes recebem.

A restrição técnica central foi identificada logo no início: a transação de mudança de status já é
pesada — atualiza o pedido, insere no histórico e ajusta estoque. Acrescentar uma chamada HTTP a ela
faria um cliente lento travar mudanças de status de outros pedidos, e um cliente fora do ar forçaria
rollback de uma operação legítima.

## Proposta técnica

### Visão geral

O fluxo se divide em duas metades independentes, ligadas por uma tabela:

1. **Produção do evento.** Na transação de `changeStatus`, depois de atualizar o pedido e o histórico,
   uma função recebe o client de transação e grava o evento em `webhook_outbox`. Se a transação falha,
   o evento desaparece com ela; se commita, o evento existe. Não há estado intermediário possível.
2. **Entrega do evento.** Um processo separado lê os pendentes mais antigos em batch, monta a
   requisição assinada e a envia ao endpoint do cliente, registrando o resultado.

### Componentes

| Componente | Responsabilidade |
| --- | --- |
| Módulo `webhooks` | CRUD de configuração de endpoints, rotação de secret, consulta de entregas |
| Tabela `webhook_outbox` | Eventos gerados, com status de processamento e payload em snapshot |
| Tabela `webhook_dead_letter` | Eventos que esgotaram as tentativas, com motivo e timestamp |
| Worker (processo separado) | Polling, entrega HTTP, assinatura, contabilização de tentativas |
| Endpoint administrativo | Replay manual de itens da DLQ, restrito a ADMIN e auditado |

### Garantias oferecidas

- **Atomicidade:** não existe pedido com status alterado cujo evento não tenha sido registrado.
- **Latência:** até 2 segundos de espera em fila, contra um teto percebido de 10 segundos.
- **Entrega:** at-least-once, com identificador estável entre tentativas.
- **Autenticidade e integridade:** assinatura HMAC-SHA256 por requisição, com secret por endpoint.
- **Ordenação:** por `order_id`, enquanto houver um único worker. **Não** há garantia de ordenação
  global — os clientes não pediram isso, e a limitação é assumida explicitamente.

### O que fica fora

Não entram nesta fase: notificação por e-mail quando um endpoint falha repetidamente, dashboard visual
para o cliente, rate limiting de saída e política de arquivamento da outbox. Os dois primeiros foram
decididos como fora de escopo; os dois últimos permanecem em aberto (adiante).

## Alternativas consideradas

### RFC-ALT-01 — Disparo HTTP síncrono dentro do `changeStatus`

Enviar a notificação na própria transação de mudança de status, sem tabela intermediária.

**Trade-off que motivou o descarte:** a transação já atualiza pedido, histórico e estoque. Uma chamada
HTTP no meio faria a latência de um cliente lento bloquear mudanças de status de outros pedidos. E com o
cliente fora do ar não haveria saída boa: ou se ignora a falha, perdendo o evento, ou se faz rollback de
uma mudança de status legítima.

### RFC-ALT-02 — Fila externa com Redis Streams

Publicar o evento em um broker dedicado, com consumidores lendo de lá.

**Trade-off que motivou o descarte:** exigiria subir e operar Redis Cluster para um time pequeno —
avaliado como overengineering. Além do custo operacional, a escrita no broker ficaria fora da transação
SQL, reintroduzindo exatamente a divergência que o outbox elimina.

### RFC-ALT-03 — Trigger de banco para acordar o worker

Evitar o polling usando um gatilho no MySQL que notificasse o processo de entrega.

**Trade-off que motivou o descarte:** o MySQL não tem listener nativo equivalente ao `NOTIFY`/`LISTEN`
do PostgreSQL. A trigger executa SQL mas não notifica processo externo; seria preciso improvisar escrita
em arquivo ou chamada a endpoint. O polling de 2 segundos atende o requisito de latência com folga.

### RFC-ALT-04 — Garantia exactly-once

Coordenar plataforma e cliente para que cada evento fosse processado uma única vez.

**Trade-off que motivou o descarte:** exigiria coordenação dos dois lados e complexidade
significativamente maior, para resolver um caso que a deduplicação por `X-Event-Id` cobre. At-least-once
com identificador de evento é o comportamento de integrações consolidadas de mercado.

## Questões em aberto

### RFC-OPEN-01 — Rate limiting de saída por cliente

Se um cliente tiver 50 pedidos mudando de status em um minuto, ele receberá 50 chamadas em sequência.
Não há hoje nenhum controle de vazão por endpoint. A decisão foi **observar e implementar se virar
problema** — mas o critério de "virar problema" não foi definido, nem quem monitora.

### RFC-OPEN-02 — Escala para múltiplos workers

A ordenação por `order_id` depende de haver um único worker processando em ordem de `created_at`. Se a
taxa de eventos exigir paralelismo, será preciso particionar por `order_id` ou usar lock pessimista.
Nenhuma das duas abordagens foi avaliada em profundidade — foi classificada como problema para depois.

### RFC-OPEN-03 — Permissão no CRUD de configuração

O replay de DLQ exige role ADMIN, mas o CRUD de configuração de webhook aceita **qualquer role
autenticada**. A posição de segurança foi que por enquanto isso basta e que mais adiante é possível
endurecer, sem definição de gatilho ou prazo para revisão.

### RFC-OPEN-04 — Retenção e arquivamento da outbox

Linhas entregues seriam arquivadas depois de cerca de 30 dias, explicitamente fora do escopo desta
feature. A tabela cresce com o volume de mudanças de status e não há responsável nem prazo definidos
para a política de retenção.

## Impacto e riscos

| Impacto | Descrição | Mitigação |
| --- | --- | --- |
| Transação de `changeStatus` | Ganha uma escrita adicional no caminho mais crítico do sistema | Inserção simples e indexada; falha derruba a transação por desenho |
| Novo processo em produção | Worker precisa ser implantado, monitorado e mantido vivo | Mesma stack e mesmo banco; observabilidade com o logger já existente |
| Crescimento de tabela | `webhook_outbox` cresce com o volume de mudanças de status | Índices em status e `created_at`; retenção em aberto (RFC-OPEN-04) |
| Exposição de dados a terceiros | Payload de pedido trafega para fora da infraestrutura | `https` obrigatório, assinatura HMAC-SHA256, payload enxuto sem itens |
| Dependência de terceiros | Indisponibilidade do cliente afeta a taxa de entrega | Retry com backoff de até cerca de 15 horas e DLQ com replay manual |
| Prazo | Três sprints, incluindo dois dias úteis de revisão de segurança | Escopo fechado; reuso máximo do que já existe |

## Decisões relacionadas

- [ADR-001 — Padrão Outbox no MySQL para publicação de eventos de pedido](adrs/ADR-001-outbox-no-mysql.md)
- [ADR-002 — Worker em processo separado com polling de 2 segundos](adrs/ADR-002-worker-em-processo-separado-com-polling.md)
- [ADR-003 — Retry com backoff exponencial e Dead Letter Queue em tabela separada](adrs/ADR-003-retry-com-backoff-e-dead-letter-queue.md)
- [ADR-004 — Autenticação HMAC-SHA256 com secret por endpoint e rotação com grace period](adrs/ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md)
- [ADR-005 — Entrega at-least-once com deduplicação por `X-Event-Id`](adrs/ADR-005-entrega-at-least-once-com-x-event-id.md)
- [ADR-006 — Reuso dos padrões existentes do projeto no módulo de webhooks](adrs/ADR-006-reuso-dos-padroes-existentes-do-projeto.md)

O detalhamento de implementação — contratos, matriz de erros, fluxos e integração com o código — está no
[FDD](FDD.md).
