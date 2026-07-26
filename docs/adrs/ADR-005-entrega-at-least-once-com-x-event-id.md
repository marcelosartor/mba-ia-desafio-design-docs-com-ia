# ADR-005: Entrega at-least-once com deduplicação por `X-Event-Id`

**Status:** Aceito
**Data:** 2026-07-26
**ADRs Relacionados:** ADR-001, ADR-003, ADR-004

## Contexto

A combinação de outbox (ADR-001) com retry (ADR-003) cria uma situação inevitável: se a chamada HTTP
chega ao cliente mas a resposta se perde, ou se o timeout de 10 segundos dispara enquanto o cliente já
processava, o worker considera falha e tenta de novo. O cliente recebe o mesmo evento duas vezes.

Garantir entrega exatamente uma vez exigiria protocolo de confirmação coordenado entre os dois lados,
com controle de estado compartilhado — complexidade que recai também sobre a implementação do cliente.

É preciso decidir qual garantia a plataforma oferece e como o cliente lida com o efeito colateral dela.

## Drivers da Decisão

- Nenhum evento pode ser perdido
- Complexidade de integração aceitável para o cliente
- Alinhamento com o que integrações de mercado já fazem, reduzindo surpresa
- Nenhum estado de coordenação adicional entre plataforma e cliente

## Decisão

A plataforma garante entrega **at-least-once**. O cliente pode receber o mesmo evento mais de uma vez e
deve estar preparado para isso.

Para viabilizar a deduplicação, cada evento carrega um **UUID gerado no momento da inserção na outbox**,
enviado no header **`X-Event-Id`**. O identificador é único por evento e estável entre tentativas: as
cinco tentativas de um mesmo evento chegam com o mesmo `X-Event-Id`.

Acompanha ainda o header `X-Webhook-Id`, com o identificador do cadastro de webhook, para que clientes
com múltiplos endpoints saibam qual configuração originou o envio.

A responsabilidade de deduplicar é do cliente, e isso é documentado de forma destacada no portal do
desenvolvedor.

## Alternativas Consideradas

### Garantia exactly-once

Coordenar plataforma e cliente para que cada evento fosse processado exatamente uma vez.

**Trade-off que motivou o descarte:** exigiria coordenação dos dois lados e aumentaria muito a
complexidade da integração, para resolver um caso que a deduplicação por identificador já cobre na
prática. At-least-once com identificador de evento é o comportamento adotado por integrações
consolidadas de mercado.

### Deduplicação do lado da plataforma

Manter registro do que já foi confirmado e suprimir reenvios.

**Trade-off que motivou o descarte:** não resolve o problema real — a ambiguidade está na resposta
perdida, e o lado que sabe se processou ou não é o cliente. A plataforma só saberia após uma confirmação
que, por definição, pode se perder também.

## Consequências

### Positivas

- Nenhum evento é perdido por ambiguidade de resposta
- Integração simples: um header e uma verificação de identificador já visto
- Comportamento previsível e familiar para quem já integrou com plataformas semelhantes
- Sem estado de coordenação adicional na plataforma

### Negativas

- Transfere ao cliente a responsabilidade de deduplicar; cliente que não implementar isso processará
  eventos repetidos
- Cliente com efeito colateral não idempotente (cobrança, envio de e-mail) pode duplicar a ação
- Exige documentação explícita e destacada, e ainda assim é fonte previsível de dúvida de integração
- A plataforma não tem como verificar se o cliente de fato deduplica

## Referências

- Fatos: F-006, F-009, F-030
- Código: `prisma/schema.prisma` (padrão de identificadores UUID no projeto)
- ADRs: ADR-001 (geração do evento na outbox), ADR-003 (retry), ADR-004 (headers e assinatura)
