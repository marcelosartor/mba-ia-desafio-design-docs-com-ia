# ADR-001: Padrão Outbox no MySQL para publicação de eventos de pedido

**Status:** Aceito
**Data:** 2026-07-26
**ADRs Relacionados:** ADR-002, ADR-005, ADR-006

## Contexto

O OMS precisa notificar clientes B2B sempre que o status de um pedido muda. Hoje não existe nenhum
mecanismo de notificação externa, evento ou fila no sistema.

A mudança de status é executada por `changeStatus`, em `src/modules/orders/order.service.ts` (l. 126–179),
dentro de uma única transação que valida a transição contra a máquina de estados, debita ou repõe
estoque, atualiza a ordem e insere o registro em `order_status_history`. Essa transação já é descrita
pelo time como pesada.

O requisito de negócio é que a notificação chegue ao cliente em menos de 10 segundos, e o requisito
técnico levantado pelo time de Pedidos é que **não pode existir caso em que o status muda e o evento não
sai**. Qualquer solução precisa resolver a atomicidade entre "mudou o status" e "o evento foi
registrado", sem acoplar a latência da transação à disponibilidade de terceiros.

## Drivers da Decisão

- Atomicidade entre a mudança de status e o registro do evento
- Nenhuma dependência de disponibilidade do cliente dentro da transação de negócio
- Time pequeno, sem apetite para operar infraestrutura adicional
- Reuso do MySQL já em produção via Prisma

## Decisão

Adotamos o **padrão Outbox** com uma tabela `webhook_outbox` no MySQL existente. A inserção do evento
acontece **dentro da mesma transação** que atualiza o pedido e o histórico de status: se a transação
commita, o evento está registrado; se faz rollback, o evento desaparece junto.

A publicação é feita por uma função `publishWebhookEvent(tx, order, fromStatus, toStatus)` que recebe o
client de transação, em vez de injetar um repository completo no `OrderService`. A entrega HTTP fica a
cargo de um processo separado (ADR-002).

A tabela tem índice no campo de status (pendente, processando, falhou, entregue) e em `created_at`, e o
consumidor lê apenas os pendentes em batches pequenos.

## Alternativas Consideradas

### Disparo HTTP síncrono dentro do `changeStatus`

Chamar o endpoint do cliente na própria transação de mudança de status.

**Trade-off que motivou o descarte:** a transação já atualiza pedido, histórico e estoque; acrescentar
uma chamada HTTP faria um cliente lento travar a mudança de status de outros pedidos. Pior: com o
cliente fora do ar, a única saída seria dar rollback em uma mudança de status legítima.

### Fila externa (Redis Streams ou equivalente)

Publicar o evento em um broker dedicado e consumir de lá.

**Trade-off que motivou o descarte:** exigiria subir e operar infraestrutura nova para um time pequeno,
e ainda assim reintroduziria o problema de atomicidade — a escrita no broker ficaria fora da transação
SQL, permitindo divergência entre o estado do pedido e o evento publicado.

## Consequências

### Positivas

- Atomicidade garantida pelo próprio banco: não existe estado em que o pedido mudou e o evento não foi
  registrado
- Nenhuma infraestrutura nova; a operação continua sendo a de um MySQL já monitorado
- A outbox serve como trilha de auditoria consultável dos eventos gerados
- A transação de negócio permanece independente da disponibilidade de terceiros

### Negativas

- A tabela cresce com o volume de mudanças de status e precisa de política de arquivamento — que ficou
  fora do escopo desta feature e sem prazo definido
- A entrega passa a depender de um segundo processo em execução; se o worker cair, os eventos se
  acumulam sem alarme próprio até que a observabilidade acuse
- Acrescenta uma escrita à transação de `changeStatus`, que já era o ponto mais pesado do fluxo
- Falha na inserção da outbox derruba a mudança de status — comportamento desejado, mas que amplia a
  superfície de falha de uma operação central do sistema

## Referências

- Fatos: F-001, F-013, F-023, F-036, F-037
- Código: `src/modules/orders/order.service.ts`, `prisma/schema.prisma`
- ADRs: ADR-002 (worker), ADR-005 (at-least-once), ADR-006 (reuso de padrões)
