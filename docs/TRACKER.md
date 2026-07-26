# Tracker de Rastreabilidade

Cada item registrado no pacote de documentos, com sua origem na transcrição da reunião ou no código
fonte da aplicação.

**Como ler:** quando `Fonte = TRANSCRICAO`, a coluna `Localização` traz o timestamp e o falante em
`TRANSCRICAO.md`. Quando `Fonte = CODIGO`, traz o caminho do arquivo no repositório.

| ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização |
| --- | --- | --- | --- | --- | --- |
| PRD-FR-01 | docs/PRD.md | Requisito Funcional | Cadastro de endpoint com URL e lista de status; secret gerada e devolvida na criação | TRANSCRICAO | [09:31] Marcos |
| PRD-FR-02 | docs/PRD.md | Requisito Funcional | Customer identificado no corpo ou no caminho, não extraído do JWT | TRANSCRICAO | [09:32] Larissa |
| PRD-FR-03 | docs/PRD.md | Requisito Funcional | Edição de endpoint já cadastrado | TRANSCRICAO | [09:33] Bruno |
| PRD-FR-04 | docs/PRD.md | Requisito Funcional | Remoção de endpoint cadastrado | TRANSCRICAO | [09:33] Bruno |
| PRD-FR-05 | docs/PRD.md | Requisito Funcional | Listagem dos endpoints de um customer | TRANSCRICAO | [09:33] Bruno |
| PRD-FR-06 | docs/PRD.md | Requisito Funcional | Seleção por endpoint de quais status geram notificação | TRANSCRICAO | [09:33] Marcos |
| PRD-FR-07 | docs/PRD.md | Requisito Funcional | Histórico das últimas 100 entregas com resultado, payload, resposta e tempo | TRANSCRICAO | [09:34] Marcos |
| PRD-FR-08 | docs/PRD.md | Requisito Funcional | Reprocessamento manual de evento que esgotou as tentativas | TRANSCRICAO | [09:35] Diego |
| PRD-FR-09 | docs/PRD.md | Requisito Funcional | Rotação de secret pela API com a anterior válida por 24 horas | TRANSCRICAO | [09:21] Sofia |
| PRD-FR-10 | docs/PRD.md | Requisito Funcional | Registro de quem solicitou o reprocessamento, para auditoria | TRANSCRICAO | [09:36] Sofia |
| PRD-FR-11 | docs/PRD.md | Requisito Funcional | Geração automática do evento na mudança de status, sem caso de status mudar sem evento | TRANSCRICAO | [09:40] Bruno |
| PRD-FR-12 | docs/PRD.md | Requisito Funcional | Reprocessamento restrito a role ADMIN | TRANSCRICAO | [09:36] Larissa |
| PRD-NFR-01 | docs/PRD.md | Requisito Não Funcional | Latência percebida abaixo de 10 segundos | TRANSCRICAO | [09:02] Marcos |
| PRD-NFR-02 | docs/PRD.md | Requisito Não Funcional | Latência de enfileiramento de até 2 segundos, aceita explicitamente | TRANSCRICAO | [09:10] Larissa |
| PRD-NFR-03 | docs/PRD.md | Requisito Não Funcional | Timeout de 10 segundos na chamada ao endpoint do cliente | TRANSCRICAO | [09:42] Diego |
| PRD-NFR-04 | docs/PRD.md | Requisito Não Funcional | Payload limitado a 64 KB, com erro acima disso | TRANSCRICAO | [09:24] Larissa |
| PRD-NFR-05 | docs/PRD.md | Requisito Não Funcional | URL obrigatoriamente https, recusando http na validação | TRANSCRICAO | [09:23] Sofia |
| PRD-NFR-06 | docs/PRD.md | Requisito Não Funcional | Códigos de erro do módulo com prefixo WEBHOOK_ | TRANSCRICAO | [09:29] Larissa |
| PRD-NFR-07 | docs/PRD.md | Requisito Não Funcional | Entrega at-least-once com identificador para deduplicação no cliente | TRANSCRICAO | [09:26] Larissa |
| PRD-NFR-08 | docs/PRD.md | Requisito Não Funcional | Ordenação por pedido enquanto houver um único worker; sem garantia global | TRANSCRICAO | [09:13] Larissa |
| PRD-OUT-01 | docs/PRD.md | Fora de Escopo | Notificação por e-mail quando o endpoint falha repetidamente, adiada | TRANSCRICAO | [09:37] Larissa |
| PRD-OUT-02 | docs/PRD.md | Fora de Escopo | Dashboard visual para o cliente, fora desta fase | TRANSCRICAO | [09:40] Larissa |
| PRD-OUT-03 | docs/PRD.md | Fora de Escopo | Rate limiting de saída por cliente, a observar | TRANSCRICAO | [09:39] Diego |
| PRD-OUT-04 | docs/PRD.md | Fora de Escopo | Arquivamento das linhas já entregues da outbox | TRANSCRICAO | [09:08] Diego |
| PRD-OUT-05 | docs/PRD.md | Fora de Escopo | Recebimento de webhooks enviados pelos clientes | TRANSCRICAO | [09:02] Marcos |
| PRD-OUT-06 | docs/PRD.md | Fora de Escopo | Garantia de ordenação global entre pedidos diferentes | TRANSCRICAO | [09:14] Marcos |
| PRD-RISK-01 | docs/PRD.md | Risco | Worker parado sem detecção enquanto a API segue respondendo | TRANSCRICAO | [09:11] Diego |
| PRD-RISK-02 | docs/PRD.md | Risco | Cliente não deduplica e processa o mesmo evento mais de uma vez | TRANSCRICAO | [09:25] Sofia |
| PRD-RISK-03 | docs/PRD.md | Risco | Endpoint permanentemente indisponível consumindo tentativas por horas | TRANSCRICAO | [09:16] Diego |
| PRD-RISK-04 | docs/PRD.md | Risco | Crescimento não controlado da tabela de eventos sem política de retenção | TRANSCRICAO | [09:07] Bruno |
| PRD-RISK-05 | docs/PRD.md | Risco | Atraso além do trimestre com risco de perda da Atlas Comercial | TRANSCRICAO | [09:00] Marcos |
| RFC-ALT-01 | docs/RFC.md | Alternativa | Disparo HTTP síncrono dentro do changeStatus, descartado | TRANSCRICAO | [09:04] Bruno |
| RFC-ALT-02 | docs/RFC.md | Alternativa | Fila externa com Redis Streams, descartada por overengineering | TRANSCRICAO | [09:07] Diego |
| RFC-ALT-03 | docs/RFC.md | Alternativa | Trigger de banco para acordar o worker, inviável no MySQL | TRANSCRICAO | [09:09] Diego |
| RFC-ALT-04 | docs/RFC.md | Alternativa | Garantia exactly-once, descartada pela complexidade bilateral | TRANSCRICAO | [09:25] Diego |
| RFC-OPEN-01 | docs/RFC.md | Questão em Aberto | Rate limiting de saída por cliente, sem critério de gatilho definido | TRANSCRICAO | [09:39] Diego |
| RFC-OPEN-02 | docs/RFC.md | Questão em Aberto | Como escalar para múltiplos workers preservando ordenação | TRANSCRICAO | [09:13] Diego |
| RFC-OPEN-03 | docs/RFC.md | Questão em Aberto | Endurecimento de permissão no CRUD de configuração | TRANSCRICAO | [09:37] Sofia |
| RFC-OPEN-04 | docs/RFC.md | Questão em Aberto | Política de retenção e arquivamento da outbox | TRANSCRICAO | [09:08] Diego |
| FDD-FLUXO-01 | docs/FDD.md | Fluxo | Publicação do evento na outbox dentro da transação de mudança de status | TRANSCRICAO | [09:06] Diego |
| FDD-FLUXO-02 | docs/FDD.md | Fluxo | Processamento pelo worker em polling de 2 segundos, em ordem de criação | TRANSCRICAO | [09:09] Diego |
| FDD-FLUXO-03 | docs/FDD.md | Fluxo | Retry com backoff 1m/5m/30m/2h/12h em até 5 tentativas | TRANSCRICAO | [09:17] Larissa |
| FDD-FLUXO-04 | docs/FDD.md | Fluxo | Movimentação para tabela de dead letter com payload, motivo e timestamp | TRANSCRICAO | [09:18] Diego |
| FDD-FLUXO-05 | docs/FDD.md | Fluxo | Replay manual recolocando o evento na outbox como pendente | TRANSCRICAO | [09:18] Diego |
| FDD-CONTRATO-01 | docs/FDD.md | Contrato | POST de cadastro de webhook com secret devolvida na criação | TRANSCRICAO | [09:31] Marcos |
| FDD-CONTRATO-02 | docs/FDD.md | Contrato | GET de listagem dos webhooks de um customer | TRANSCRICAO | [09:33] Bruno |
| FDD-CONTRATO-03 | docs/FDD.md | Contrato | PATCH de edição de endpoint | TRANSCRICAO | [09:33] Bruno |
| FDD-CONTRATO-04 | docs/FDD.md | Contrato | Rotação de secret com a anterior válida por 24 horas | TRANSCRICAO | [09:21] Sofia |
| FDD-CONTRATO-05 | docs/FDD.md | Contrato | GET /webhooks/:id/deliveries com as últimas 100 entregas | TRANSCRICAO | [09:34] Marcos |
| FDD-CONTRATO-06 | docs/FDD.md | Contrato | POST /admin/webhooks/dead-letter/:id/replay restrito a ADMIN | TRANSCRICAO | [09:35] Diego |
| FDD-CONTRATO-07 | docs/FDD.md | Contrato | Payload e headers da requisição de entrega ao cliente | TRANSCRICAO | [09:43] Diego |
| FDD-ERRO-01 | docs/FDD.md | Erro | WEBHOOK_NOT_FOUND para endpoint inexistente | TRANSCRICAO | [09:28] Bruno |
| FDD-ERRO-02 | docs/FDD.md | Erro | WEBHOOK_INVALID_URL para URL ausente, malformada ou sem https | TRANSCRICAO | [09:28] Bruno |
| FDD-ERRO-03 | docs/FDD.md | Erro | WEBHOOK_SECRET_REQUIRED quando falta secret vigente | TRANSCRICAO | [09:28] Bruno |
| FDD-ERRO-04 | docs/FDD.md | Erro | WEBHOOK_INVALID_STATUS_FILTER para status fora do enum | TRANSCRICAO | [09:33] Marcos |
| FDD-ERRO-05 | docs/FDD.md | Erro | WEBHOOK_DEAD_LETTER_NOT_FOUND no replay de item inexistente | TRANSCRICAO | [09:35] Diego |
| FDD-ERRO-06 | docs/FDD.md | Erro | WEBHOOK_PAYLOAD_TOO_LARGE acima de 64 KB, com erro em vez de truncamento | TRANSCRICAO | [09:24] Larissa |
| FDD-ERRO-07 | docs/FDD.md | Erro | WEBHOOK_DELIVERY_TIMEOUT quando o cliente não responde em 10 segundos | TRANSCRICAO | [09:42] Diego |
| FDD-ERRO-08 | docs/FDD.md | Erro | WEBHOOK_DELIVERY_FAILED para resposta fora de 2xx ou erro de rede | TRANSCRICAO | [09:15] Diego |
| FDD-ERRO-09 | docs/FDD.md | Erro | WEBHOOK_MAX_ATTEMPTS_EXCEEDED ao esgotar a quinta tentativa | TRANSCRICAO | [09:17] Larissa |
| FDD-INT-01 | docs/FDD.md | Restrição | Publicação do evento dentro da transação do changeStatus | CODIGO | src/modules/orders/order.service.ts |
| FDD-INT-02 | docs/FDD.md | Decisão | Erros do módulo estendendo a hierarquia de AppError existente | CODIGO | src/shared/errors/http-errors.ts |
| FDD-INT-03 | docs/FDD.md | Decisão | Middleware de erro centralizado reaproveitado sem alteração | CODIGO | src/middlewares/error.middleware.ts |
| FDD-INT-04 | docs/FDD.md | Decisão | requireRole ADMIN aplicado apenas ao endpoint de replay | CODIGO | src/middlewares/auth.middleware.ts |
| FDD-INT-05 | docs/FDD.md | Restrição | Filtro de status validado contra o enum da máquina de estados | CODIGO | src/modules/orders/order.status.ts |
| FDD-INT-06 | docs/FDD.md | Decisão | Logger Pino e envelope paginado reaproveitados no módulo e no worker | CODIGO | src/shared/logger/index.ts |
| FDD-INT-07 | docs/FDD.md | Decisão | Montagem do roteador do módulo no padrão dos demais domínios | CODIGO | src/routes/index.ts |
| FDD-INT-08 | docs/FDD.md | Decisão | Novas tabelas com identificadores UUID no schema Prisma | CODIGO | prisma/schema.prisma |
| ADR-001 | docs/adrs/ADR-001-outbox-no-mysql.md | Decisão | Padrão Outbox no MySQL com inserção na mesma transação | TRANSCRICAO | [09:06] Diego |
| ADR-002 | docs/adrs/ADR-002-worker-em-processo-separado-com-polling.md | Decisão | Worker em processo separado com polling de 2 segundos | TRANSCRICAO | [09:11] Diego |
| ADR-003 | docs/adrs/ADR-003-retry-com-backoff-e-dead-letter-queue.md | Decisão | Retry com backoff em 5 tentativas e DLQ em tabela separada | TRANSCRICAO | [09:17] Larissa |
| ADR-004 | docs/adrs/ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md | Decisão | HMAC-SHA256 com secret por endpoint e rotação com grace de 24 horas | TRANSCRICAO | [09:22] Sofia |
| ADR-005 | docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md | Decisão | Entrega at-least-once com deduplicação por X-Event-Id | TRANSCRICAO | [09:26] Larissa |
| ADR-006 | docs/adrs/ADR-006-reuso-dos-padroes-existentes-do-projeto.md | Decisão | Reuso integral dos padrões existentes do projeto | TRANSCRICAO | [09:30] Larissa |

## Cobertura

| Métrica | Valor |
| --- | --- |
| Itens rastreados | 74 |
| Origem `TRANSCRICAO` | 66 linhas (89%) |
| Origem `CODIGO` | 8 linhas (11%) |
| Documentos cobertos | PRD, RFC, FDD e os 6 ADRs |

### Itens deliberadamente não rastreados

Decisões secundárias registradas apenas no FDD, sem ID próprio, mas com origem identificada na
transcrição: payload em snapshot na inserção ([09:52] Larissa), identificadores em UUID
([09:51] Larissa), índices da outbox em status e data de criação ([09:08] Diego), instância própria de
PrismaClient no worker ([09:30] Bruno) e filtro de status aplicado na inserção ([09:34] Bruno).
