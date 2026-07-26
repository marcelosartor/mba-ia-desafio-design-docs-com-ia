# ADR-003: Retry com backoff exponencial e Dead Letter Queue em tabela separada

**Status:** Aceito
**Data:** 2026-07-26
**ADRs Relacionados:** ADR-002, ADR-005

## Contexto

A entrega de webhooks depende da disponibilidade de um endpoint fora da nossa infraestrutura. Falhas
não são exceção: clientes ficam indisponíveis por manutenção planejada, deploys e incidentes. O time
relata cliente com indisponibilidade de duas horas em manutenção programada.

Sem política de retry, uma janela curta de indisponibilidade do cliente resultaria em perda definitiva
de notificação. Com retry mal calibrado, eventos ficariam pendurados indefinidamente ou seriam
descartados cedo demais.

É preciso também definir o destino do evento que esgota as tentativas: ele não pode simplesmente sumir,
porque a operação precisa investigar e reprocessar.

## Drivers da Decisão

- Cobrir janelas reais de indisponibilidade de cliente, na ordem de horas
- Não manter evento em tentativa perpétua quando o endpoint foi abandonado
- Preservar o evento que falhou definitivamente, com contexto suficiente para diagnóstico
- Manter a leitura da outbox principal limpa e barata

## Decisão

Adotamos **retry com backoff exponencial em 5 tentativas**, com os intervalos **1 minuto, 5 minutos,
30 minutos, 2 horas e 12 horas** — cerca de 15 horas entre a primeira falha e a última tentativa.

Chamada que não responde dentro de **10 segundos** é tratada como falha e entra no ciclo de retry.

Esgotadas as cinco tentativas, o evento é movido para uma tabela separada, `webhook_dead_letter`,
contendo o payload, o motivo da falha e o timestamp.

O reprocessamento é **manual**, via endpoint administrativo `POST /admin/webhooks/dead-letter/:id/replay`,
que recoloca o evento na outbox como pendente.

## Alternativas Consideradas

### Retry indefinido com backoff

Continuar tentando enquanto o evento não for entregue, com intervalos sempre crescentes.

**Trade-off que motivou o descarte:** um cliente que desativou o endpoint sem avisar deixaria eventos
pendurados para sempre, consumindo recursos do worker e poluindo a outbox sem nenhuma chance de sucesso.

### Teto de 3 tentativas

Política mais agressiva, encerrando a entrega mais cedo.

**Trade-off que motivou o descarte:** três tentativas cobrem cerca de 30 minutos. Um cliente que tenha
indisponibilidade de manhã perderia o evento antes de voltar — cenário já observado com indisponibilidade
planejada de duas horas.

### DLQ como flag `failed` na própria outbox

Marcar o evento como falho na tabela principal, sem tabela adicional.

**Trade-off que motivou o descarte:** misturaria eventos ativos e mortos na mesma tabela lida pelo worker
a cada 2 segundos, encarecendo a consulta principal e dificultando a inspeção do que falhou de vez.

## Consequências

### Positivas

- Cobre janelas de indisponibilidade de até cerca de 15 horas sem intervenção humana
- Nenhum evento é perdido silenciosamente: o que falha em definitivo fica persistido com motivo
- A outbox principal permanece enxuta, com a consulta do worker restrita a eventos ativos
- O replay manual dá à operação um caminho explícito de recuperação

### Negativas

- Um evento pode levar até cerca de 15 horas para ser considerado definitivamente perdido — bem além do
  "tempo real" prometido, ainda que apenas em cenário de falha
- Reprocessamento é manual: exige alguém percebendo a DLQ e agindo, sem alerta automático nesta fase
- Uma tabela adicional para modelar, migrar e manter
- Com intervalos longos, um cliente que volta logo após uma falha ainda espera o próximo passo do
  backoff, sem mecanismo de retentativa antecipada

## Referências

- Fatos: F-003, F-004, F-020, F-026
- Código: `src/middlewares/auth.middleware.ts` (proteção do endpoint de replay)
- ADRs: ADR-002 (worker), ADR-005 (at-least-once)
