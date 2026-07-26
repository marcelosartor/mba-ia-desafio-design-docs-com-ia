# PRD: Sistema de Webhooks de Notificação de Pedidos

| Campo | Valor |
| --- | --- |
| **Versão** | 1.0 |
| **Data** | 2026-07-26 |
| **Responsável** | Marcos (Product Manager) |
| **Documentos relacionados** | [RFC](RFC.md) · [FDD](FDD.md) · [ADRs](adrs/) |

## 1. Resumo e contexto da feature

O OMS passa a notificar clientes B2B automaticamente sempre que o status de um pedido muda. Em vez de
consultar a API repetidamente para descobrir se algo mudou, o cliente cadastra um endpoint HTTP e recebe
uma requisição assinada a cada transição de status que lhe interessa.

O cliente configura seus endpoints pela própria API do OMS, escolhe quais status quer receber, consulta
o histórico das entregas e pode rotacionar a credencial de assinatura quando precisar. Entregas que
falham são retentadas automaticamente ao longo de aproximadamente 15 horas; o que falha em definitivo
fica registrado para reprocessamento manual pela operação.

## 2. Problema e motivação

Três clientes B2B — Atlas Comercial, MaxDistribuição e Nova Cargo — fizeram pedido formal de notificação
em tempo real das mudanças de status dos pedidos deles.

Hoje esses clientes fazem polling em `GET /orders` de tempos em tempos para descobrir se algo mudou.
A consequência é dupla: a integração fica lenta, porque a informação só chega no próximo ciclo de
consulta, e cara, porque exige requisições contínuas independentemente de haver mudança.

A Atlas Comercial sinalizou que pode migrar para um concorrente caso a entrega não saia até o fim do
trimestre — o que transforma um pedido de melhoria de integração em risco de perda de receita.

## 3. Público-alvo e cenários de uso

| Público | Cenário |
| --- | --- |
| Cliente B2B integrado (Atlas, MaxDistribuição, Nova Cargo) | Recebe notificação assinada quando um pedido seu muda de status e atualiza o próprio sistema sem consultar a API |
| Time de integração do cliente | Cadastra e mantém os endpoints, escolhe os status de interesse e rotaciona a secret periodicamente |
| Time de integração do cliente (diagnóstico) | Consulta o histórico das últimas entregas para investigar por que um evento não foi processado do lado dele |
| Operação do OMS (role ADMIN) | Reprocessa eventos que esgotaram as tentativas de entrega |

## 4. Objetivos e métricas de sucesso

| # | Objetivo | Métrica | Meta |
| --- | --- | --- | --- |
| 1 | Entregar a notificação em tempo percebido como real | Latência entre a mudança de status e a chegada da requisição ao cliente | Abaixo de 10 segundos |
| 2 | Manter a latência de enfileiramento previsível | Tempo de espera do evento na outbox em condição normal | Até 2 segundos |
| 3 | Não perder eventos por indisponibilidade do cliente | Janela de retry antes de considerar falha definitiva | Cerca de 15 horas, em 5 tentativas |
| 4 | Eliminar a necessidade de polling do lado do cliente | Clientes com endpoint ativo entre os três solicitantes | 3 de 3 |

A meta de 10 segundos vem do próprio cliente: qualquer coisa abaixo disso é considerada tempo real, e o
que importa é que a informação não fique pendurada exigindo atualização manual.

## 5. Escopo

### Incluso

- Cadastro, edição, remoção e listagem de endpoints de webhook por customer
- Seleção, por endpoint, de quais status de pedido geram notificação
- Envio automático da notificação a cada mudança de status assinada com HMAC-SHA256
- Rotação de secret pela API, com validade paralela de 24 horas para a credencial anterior
- Consulta do histórico das últimas 100 entregas de um endpoint
- Reprocessamento manual, restrito a ADMIN, de eventos que esgotaram as tentativas

### Fora de escopo

| ID | Item | Situação | Motivo | Origem |
| --- | --- | --- | --- | --- |
| PRD-OUT-01 | Notificação por e-mail ao cliente quando o endpoint falha repetidamente | Adiado | Fica para a próxima fase, após medir o impacto da entrega atual | [09:37] Larissa |
| PRD-OUT-02 | Dashboard visual para o cliente acompanhar seus webhooks | Descartado desta fase | Projeto separado do time de frontend; agora só endpoints | [09:40] Larissa |
| PRD-OUT-03 | Rate limiting de saída por cliente | Adiado | Observar e implementar se virar problema — ver [RFC-OPEN-01](RFC.md#rfc-open-01--rate-limiting-de-saída-por-cliente) | [09:39] Diego |
| PRD-OUT-04 | Arquivamento de linhas já entregues da outbox | Fora do escopo | Declarado explicitamente fora do escopo desta feature — ver [RFC-OPEN-04](RFC.md#rfc-open-04--retenção-e-arquivamento-da-outbox) | [09:08] Diego |
| PRD-OUT-05 | Recebimento de webhooks enviados pelos clientes (inbound) | Descartado | Os clientes querem receber, não mandar | [09:02] Marcos |
| PRD-OUT-06 | Garantia de ordenação global entre pedidos diferentes | Descartado | Os clientes nunca pediram; só interessa saber se cada pedido mudou | [09:14] Marcos |

## 6. Requisitos funcionais

| ID | Requisito | Origem |
| --- | --- | --- |
| PRD-FR-01 | O sistema deve permitir cadastrar um endpoint de webhook informando URL e a lista de status de interesse, gerando e devolvendo a secret na criação | [09:31] Marcos |
| PRD-FR-02 | O cadastro deve identificar o customer explicitamente no corpo ou no caminho da requisição, e não a partir do JWT | [09:32] Larissa |
| PRD-FR-03 | O sistema deve permitir editar um endpoint já cadastrado | [09:33] Bruno |
| PRD-FR-04 | O sistema deve permitir remover um endpoint cadastrado | [09:33] Bruno |
| PRD-FR-05 | O sistema deve permitir listar os endpoints de um customer | [09:33] Bruno |
| PRD-FR-06 | Cada endpoint deve poder escolher quais status de pedido geram notificação | [09:33] Marcos |
| PRD-FR-07 | O sistema deve expor o histórico das últimas 100 entregas de um endpoint, com resultado, payload, resposta e tempo de resposta | [09:34] Marcos |
| PRD-FR-08 | O sistema deve permitir reprocessar manualmente um evento que esgotou as tentativas, recolocando-o na fila de entrega | [09:35] Diego |
| PRD-FR-09 | O cliente deve poder solicitar uma nova secret pela API, mantendo a anterior válida por 24 horas | [09:21] Sofia |
| PRD-FR-10 | O reprocessamento manual deve registrar quem o solicitou, para auditoria | [09:36] Sofia |
| PRD-FR-11 | A notificação deve ser gerada automaticamente a cada mudança de status, sem caso em que o status muda e o evento não é registrado | [09:40] Bruno |
| PRD-FR-12 | O reprocessamento manual deve ser restrito a usuários com role ADMIN | [09:36] Larissa |

## 7. Requisitos não funcionais

| ID | Requisito | Valor | Origem |
| --- | --- | --- | --- |
| PRD-NFR-01 | Latência percebida entre a mudança de status e a notificação | Abaixo de 10 segundos | [09:02] Marcos |
| PRD-NFR-02 | Latência de enfileiramento aceita no pior caso | 2 segundos | [09:10] Larissa |
| PRD-NFR-03 | Timeout da chamada ao endpoint do cliente | 10 segundos | [09:42] Diego |
| PRD-NFR-04 | Tamanho máximo do payload de um evento | 64 KB, com erro acima disso | [09:24] Larissa |
| PRD-NFR-05 | Protocolo obrigatório da URL cadastrada | `https`, recusando `http` na validação | [09:23] Sofia |
| PRD-NFR-06 | Padrão dos códigos de erro do módulo | Prefixo `WEBHOOK_` | [09:29] Larissa |
| PRD-NFR-07 | Garantia de entrega | At-least-once, com identificador de evento para deduplicação no cliente | [09:26] Larissa |
| PRD-NFR-08 | Ordenação das notificações | Por pedido, enquanto houver um único worker; sem garantia global | [09:13] Larissa |

## 8. Decisões e trade-offs principais

| Decisão | Trade-off aceito | ADR |
| --- | --- | --- |
| Evento gravado na mesma transação da mudança de status | Uma escrita a mais no caminho mais crítico do sistema | [ADR-001](adrs/ADR-001-outbox-no-mysql.md) |
| Entrega por processo separado em polling de 2 segundos | Latência mínima de 2 segundos e um processo a mais para operar | [ADR-002](adrs/ADR-002-worker-em-processo-separado-com-polling.md) |
| Cinco tentativas ao longo de cerca de 15 horas, depois DLQ | Um evento pode levar até 15 horas para ser considerado perdido, e o reprocessamento é manual | [ADR-003](adrs/ADR-003-retry-com-backoff-e-dead-letter-queue.md) |
| Secret única por endpoint, com rotação e grace period de 24 h | Duas credenciais válidas convivem por 24 horas | [ADR-004](adrs/ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md) |
| Entrega at-least-once | O cliente precisa deduplicar; efeito colateral não idempotente do lado dele pode duplicar | [ADR-005](adrs/ADR-005-entrega-at-least-once-com-x-event-id.md) |
| Reuso integral dos padrões do projeto | O módulo herda as limitações dos padrões atuais | [ADR-006](adrs/ADR-006-reuso-dos-padroes-existentes-do-projeto.md) |

## 9. Dependências

- **Revisão de segurança:** dois dias úteis reservados para revisão do código de geração de secret e
  assinatura HMAC antes do deploy, conforme acordado com a engenharia de segurança
- **Documentação para o cliente:** o comportamento at-least-once e a necessidade de deduplicação por
  `X-Event-Id` precisam estar documentados no portal do desenvolvedor antes da liberação
- **Comunicação com os clientes:** confirmação de prazo com Atlas, MaxDistribuição e Nova Cargo
- **Infraestrutura:** o processo do worker precisa ser implantado e supervisionado, além da API
- **Prazo:** três sprints, já incluindo a revisão de segurança ao final

## 10. Riscos e mitigação

| ID | Risco | Probabilidade | Impacto | Mitigação |
| --- | --- | --- | --- | --- |
| PRD-RISK-01 | Worker parado sem detecção: eventos se acumulam e nenhum cliente é notificado, enquanto a API segue respondendo normalmente | Média | Alto — a feature deixa de funcionar sem sinal visível para o usuário | Alerta sobre o atraso da fila e supervisão do processo; os eventos pendentes são processados na ordem ao reiniciar, sem perda |
| PRD-RISK-02 | Cliente não implementa deduplicação por `X-Event-Id` e processa o mesmo evento mais de uma vez | Média | Médio — pode gerar ação duplicada no sistema do cliente | Documentação destacada no portal do desenvolvedor; identificador estável entre tentativas e no replay |
| PRD-RISK-03 | Endpoint de cliente permanentemente indisponível consome cinco tentativas por evento durante cerca de 15 horas | Média | Médio — worker ocupado com trabalho inútil e atraso na entrega dos demais | Métrica de tentativas por endpoint evidencia o caso; endpoint pode ser desativado pela API |
| PRD-RISK-04 | Crescimento não controlado da tabela de eventos, sem política de retenção definida | Alta no médio prazo | Médio — degradação da consulta do worker e consumo de disco | Índices em status e data de criação, leitura em batch pequeno; definir a política de retenção, hoje em aberto |
| PRD-RISK-05 | Atraso na entrega além do fim do trimestre | Baixa | Alto — a Atlas Comercial sinalizou possibilidade de migrar para o concorrente | Escopo fechado com itens explicitamente adiados; reuso máximo do que já existe no projeto |

## 11. Critérios de aceitação

- [ ] Um cliente consegue cadastrar um endpoint e recebe a secret na resposta da criação
- [ ] A notificação chega ao endpoint em menos de 10 segundos após a mudança de status
- [ ] Apenas os status selecionados no cadastro geram notificação
- [ ] A requisição chega assinada e o cliente consegue validar a assinatura com a secret recebida
- [ ] Um endpoint indisponível recebe cinco tentativas antes de o evento ser considerado perdido
- [ ] O evento que esgota as tentativas fica disponível para reprocessamento manual
- [ ] Somente usuário ADMIN consegue reprocessar
- [ ] O cliente consegue consultar as últimas 100 entregas do endpoint dele
- [ ] Rotacionar a secret não interrompe as entregas em andamento durante 24 horas
- [ ] Cadastro com URL `http` é recusado

```gherkin
Cenário: notificação de mudança de status para endpoint interessado
  Dado que o cliente tem um endpoint ativo assinando os status SHIPPED e DELIVERED
  Quando um pedido desse cliente passa de PROCESSING para SHIPPED
  Então o endpoint recebe uma requisição assinada em até 10 segundos
  E o corpo informa from_status PROCESSING e to_status SHIPPED

Cenário: status não assinado não gera notificação
  Dado que o cliente tem um endpoint ativo assinando apenas DELIVERED
  Quando um pedido desse cliente passa de PENDING para PAID
  Então nenhuma requisição é enviada ao endpoint

Cenário: reprocessamento restrito a ADMIN
  Dado um evento que esgotou as cinco tentativas de entrega
  Quando um usuário com role OPERATOR solicita o reprocessamento
  Então a operação é recusada por falta de permissão
```

## 12. Estratégia de testes e validação

| Camada | O que valida |
| --- | --- |
| Testes de integração do pedido | Que a falha ao registrar o evento reverte a mudança de status, e que status não assinado não gera evento |
| Testes de contrato da API | Cadastro, edição, remoção, listagem, rotação de secret, histórico de entregas e recusa de URL `http` |
| Testes do worker | Sucesso, falha, timeout, progressão das cinco tentativas e movimentação para a fila de falhas definitivas |
| Testes de segurança | Assinatura conferindo com a secret do endpoint, validade da secret anterior durante o grace period, ausência da secret nas respostas de leitura |
| Testes de autorização | Reprocessamento negado para role não-ADMIN e registro de auditoria quando permitido |
| Validação com o cliente | Envio de eventos de teste para os endpoints de homologação de Atlas, MaxDistribuição e Nova Cargo antes da liberação |
| Revisão de segurança | Dois dias úteis de revisão do código de geração de secret e assinatura antes do deploy |
