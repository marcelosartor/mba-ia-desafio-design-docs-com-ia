# Architectural Decision Records

Este diretório armazena os ADRs (Architectural Decision Records) do projeto. Cada decisão arquitetural
relevante é registrada em um arquivo individual, no formato MADR, nomeado
`ADR-NNN-titulo-em-kebab-case.md` com numeração sequencial.

Seções de cada ADR: **Status**, **Contexto**, **Drivers da Decisão**, **Decisão**,
**Alternativas Consideradas** (cada uma com o trade-off que motivou o descarte), **Consequências**
(positivas e negativas) e **Referências**.

## Índice

| ADR | Decisão | Status |
| --- | --- | --- |
| [ADR-001](ADR-001-outbox-no-mysql.md) | Padrão Outbox no MySQL para publicação de eventos de pedido | Aceito |
| [ADR-002](ADR-002-worker-em-processo-separado-com-polling.md) | Worker em processo separado com polling de 2 segundos | Aceito |
| [ADR-003](ADR-003-retry-com-backoff-e-dead-letter-queue.md) | Retry com backoff exponencial e Dead Letter Queue em tabela separada | Aceito |
| [ADR-004](ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md) | Autenticação HMAC-SHA256 com secret por endpoint e rotação com grace period | Aceito |
| [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md) | Entrega at-least-once com deduplicação por `X-Event-Id` | Aceito |
| [ADR-006](ADR-006-reuso-dos-padroes-existentes-do-projeto.md) | Reuso dos padrões existentes do projeto no módulo de webhooks | Aceito |

Sugestão de leitura: comece pelo ADR-001, que sustenta os demais.

A proposta técnica que consolida estas decisões está no [RFC](../RFC.md); o detalhamento de
implementação, no [FDD](../FDD.md); a origem de cada item, no [Tracker](../TRACKER.md).
