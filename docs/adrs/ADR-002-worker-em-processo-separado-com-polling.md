# ADR-002: Worker em processo separado com polling de 2 segundos

**Status:** Aceito
**Data:** 2026-07-26
**ADRs Relacionados:** ADR-001, ADR-003

## Contexto

Com o padrão Outbox definido (ADR-001), os eventos ficam registrados em `webhook_outbox` aguardando
entrega. Falta decidir **quem** lê essa tabela e dispara as chamadas HTTP, e **onde** esse componente
executa.

Duas restrições delimitam o espaço de solução. A primeira é de negócio: os clientes consideram "tempo
real" qualquer latência abaixo de 10 segundos. A segunda é operacional: a API é reiniciada com
frequência normal de deploy, e um consumidor embutido nela seria interrompido a cada reinício.

O banco é MySQL, o que elimina mecanismos de notificação assíncrona disponíveis em outros SGBDs.

## Drivers da Decisão

- Latência de entrega bem abaixo do teto de 10 segundos percebido pelo cliente
- Independência do ciclo de vida da API
- Limitação do MySQL quanto a notificação de processos externos
- Reuso da mesma stack e do mesmo banco, sem componente novo

## Decisão

O consumidor da outbox é um **processo separado**, com entry-point próprio (proposto: `src/worker.ts`),
espelhando o `src/server.ts` existente, e script `npm run worker`. Ele executa **polling em loop a cada
2 segundos**, buscando os eventos pendentes mais antigos, processando e marcando o resultado.

O worker abre a **própria instância de `PrismaClient`**, apontando para o mesmo banco e a mesma
`DATABASE_URL`, porque o client é por processo.

Nesta fase roda um único worker. A ordenação de entrega é por `order_id`, decorrente do processamento em
ordem de `created_at`, e vale enquanto houver um só processo — registrada como limitação conhecida, não
como garantia.

## Alternativas Consideradas

### Consumidor embutido na instância da API

Rodar o loop de entrega dentro do mesmo processo Node que serve as requisições HTTP.

**Trade-off que motivou o descarte:** a cada reinício da API o consumidor morre junto, e a entrega passa
a depender do ciclo de deploy. Além disso, a carga de entrega competiria com o atendimento das
requisições no mesmo event loop.

### Trigger de banco notificando o worker

Usar um gatilho no MySQL para acordar o processo de entrega assim que o evento fosse inserido, evitando
o polling.

**Trade-off que motivou o descarte:** o MySQL não tem listener nativo equivalente ao `NOTIFY`/`LISTEN`
do PostgreSQL. A trigger executa SQL, mas não notifica processo externo — seria preciso improvisar
escrita em arquivo ou chamada a um endpoint. O polling de 2 segundos atende o requisito de latência sem
essa complexidade.

## Consequências

### Positivas

- O consumidor sobrevive a reinícios e deploys da API
- Latência de entrega dominada pelo intervalo de polling, com folga de uma ordem de grandeza sobre o
  teto de 10 segundos
- Nenhuma tecnologia nova: mesmo Node, mesmo Prisma, mesmo banco
- Isolamento de falha: um erro no loop de entrega não derruba a API

### Negativas

- Latência mínima de 2 segundos no pior caso, aceita explicitamente pelo time
- Polling consulta o banco continuamente, mesmo sem eventos pendentes
- Passa a existir um segundo processo para implantar, monitorar e manter vivo
- Com um único worker, a taxa de entrega não escala horizontalmente; escalar exigiria particionamento
  por `order_id` ou lock pessimista, o que sacrificaria a ordenação atual e permanece em aberto

## Referências

- Fatos: F-002, F-014, F-025, F-033, F-040
- Código: `src/server.ts`, `package.json`, `src/config/env.ts`
- ADRs: ADR-001 (outbox), ADR-003 (retry e DLQ)
