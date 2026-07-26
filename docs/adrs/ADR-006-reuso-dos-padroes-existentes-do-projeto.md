# ADR-006: Reuso dos padrões existentes do projeto no módulo de webhooks

**Status:** Aceito
**Data:** 2026-07-26
**ADRs Relacionados:** ADR-001, ADR-002, ADR-004

## Contexto

O OMS tem convenções estabelecidas e uniformes entre os cinco domínios já implementados. Cada domínio é
um módulo em `src/modules/<dominio>` com controller, service, repository, routes e schemas. Os erros
derivam de `AppError` em `src/shared/errors/app-error.ts`, com código textual por caso, e são
serializados pelo middleware centralizado em `src/middlewares/error.middleware.ts`. A autorização usa
`authenticate` e `requireRole` de `src/middlewares/auth.middleware.ts`. O logging é Pino, configurado em
`src/shared/logger/index.ts` com redação de campos sensíveis. A validação de entrada é feita com Zod
através de `src/middlewares/validate.middleware.ts`.

A feature de webhooks introduz um domínio novo e um processo novo. A escolha é entre seguir essas
convenções ou tratar o módulo como território separado, com padrões próprios.

## Drivers da Decisão

- Previsibilidade para quem já trabalha na base
- Nenhuma dependência ou abstração nova sem necessidade demonstrada
- Aproveitamento do que já está testado em produção
- Prazo de três sprints, com revisão de segurança no fim

## Decisão

O módulo de webhooks segue integralmente os padrões existentes:

- **Estrutura:** `src/modules/webhooks` com controller, service, repository, routes e schemas, igual aos
  demais domínios. A lógica de processamento do worker fica em um arquivo do próprio módulo.
- **Erros:** classes estendendo `AppError`, com códigos no prefixo `WEBHOOK_` — `WEBHOOK_NOT_FOUND`,
  `WEBHOOK_INVALID_URL`, `WEBHOOK_SECRET_REQUIRED` e demais casos do módulo.
- **Tratamento de erro HTTP:** o middleware centralizado existente, **sem nenhuma alteração** — ele já
  serializa `AppError`, `ZodError` e erros conhecidos do Prisma.
- **Logging:** o logger Pino já configurado, incluindo no worker. Nada novo é introduzido.
- **Validação:** schemas Zod via middleware `validate`, incluindo a exigência de URL `https`.
- **Autorização:** `authenticate` em todo o módulo e **`requireRole('ADMIN')`** no endpoint de replay de
  DLQ, reaproveitando o helper existente.
- **Identificadores:** UUID, como no restante do projeto.
- **Resposta paginada:** `paginated()` de `src/shared/http/response.ts` nas listagens.

## Alternativas Consideradas

### Módulo com padrões próprios

Tratar webhooks como subsistema independente, com sua própria hierarquia de erros, seu próprio logger e
suas próprias convenções de resposta.

**Trade-off que motivou o descarte:** criaria duas gramáticas dentro da mesma base, obrigando quem
mantém o sistema a aprender qual convenção vale em cada pasta. O ganho seria autonomia que ninguém pediu,
ao custo de manutenção permanente.

### Abstrair uma camada genérica de notificações

Antecipar futuros canais (e-mail, SMS) criando uma abstração de entrega antes de haver um segundo canal.

**Trade-off que motivou o descarte:** o único canal desta fase é webhook — e-mail foi explicitamente
adiado. Abstrair sobre um caso único produziria indireção sem informação suficiente para acertar a
interface.

## Consequências

### Positivas

- Quem conhece qualquer módulo do projeto entende o de webhooks sem contexto adicional
- Nenhuma alteração necessária no middleware de erro, no logger ou na infraestrutura de autenticação
- Menos código novo para escrever, revisar e testar dentro do prazo de três sprints
- A revisão de segurança se concentra no que é realmente novo — geração de secret e assinatura HMAC —
  em vez de reavaliar infraestrutura já validada

### Negativas

- O módulo herda as limitações dos padrões atuais; uma inadequação existente é replicada em vez de
  corrigida
- Uma futura necessidade legítima de divergir encontrará resistência de consistência
- O padrão de módulo foi desenhado para domínios servidos por HTTP; o worker é um processo com ciclo de
  vida diferente e se encaixa nele apenas parcialmente

## Referências

- Fatos: F-007, F-011, F-012, F-029, F-038, F-039
- Código: `src/modules/orders/order.routes.ts`, `src/shared/errors/app-error.ts`,
  `src/shared/errors/http-errors.ts`, `src/middlewares/error.middleware.ts`,
  `src/middlewares/auth.middleware.ts`, `src/shared/logger/index.ts`, `src/shared/http/response.ts`
- ADRs: ADR-001 (integração na transação), ADR-002 (worker), ADR-004 (segurança)
