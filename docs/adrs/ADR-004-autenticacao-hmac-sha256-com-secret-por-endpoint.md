# ADR-004: Autenticação HMAC-SHA256 com secret por endpoint e rotação com grace period

**Status:** Aceito
**Data:** 2026-07-26
**ADRs Relacionados:** ADR-005, ADR-006

## Contexto

A feature expõe dados de pedidos a endpoints HTTP que estão fora da nossa infraestrutura. Do lado do
cliente, duas garantias são necessárias: que a requisição veio realmente da nossa plataforma, e que o
payload não foi adulterado no caminho.

O time de segurança levanta ainda um cenário concreto já observado: cliente que vazou secret em log de
aplicação. Isso torna o raio de alcance de um vazamento uma preocupação de projeto, não hipotética.

Como os endpoints são cadastrados e mantidos pelos próprios clientes, qualquer esquema de credencial
precisa admitir troca sem janela de indisponibilidade — o cliente precisa de tempo para atualizar os
sistemas dele.

## Drivers da Decisão

- Autenticidade e integridade verificáveis pelo cliente, sem estado compartilhado
- Contenção do impacto de um vazamento de credencial
- Troca de credencial sem interromper a entrega
- Adoção trivial pelo cliente, com bibliotecas disponíveis em qualquer linguagem

## Decisão

Assinamos o corpo do request com **HMAC-SHA256** e enviamos a assinatura no header `X-Signature`. O
cliente recalcula a assinatura do lado dele e compara.

Cada endpoint de webhook tem uma **secret única**, gerada pela plataforma e devolvida na criação do
cadastro. Não existe secret global da plataforma.

A secret é **rotacionável pela API**. Durante a rotação, a secret antiga permanece válida por
**24 horas** em paralelo com a nova; encerrado o grace period, a antiga é invalidada.

Complementarmente, a URL cadastrada deve ser `https` — validação no schema Zod, com recusa no cadastro
caso contrário. O header `X-Timestamp` acompanha o envio, permitindo ao cliente detectar tentativa de
replay se optar por isso.

## Alternativas Consideradas

### Secret global da plataforma

Uma única chave compartilhada com todos os clientes.

**Trade-off que motivou o descarte:** o vazamento de uma credencial comprometeria todos os clientes de
uma vez, e a rotação exigiria coordenação simultânea com toda a base — inviável na prática.

### Rotação imediata, sem grace period

Invalidar a secret antiga no instante em que a nova é emitida.

**Trade-off que motivou o descarte:** criaria janela de falha de entrega para todo cliente que não
atualizasse os sistemas no mesmo instante da rotação, transformando uma operação de higiene de segurança
em incidente de integração.

## Consequências

### Positivas

- Vazamento fica contido a um único endpoint de um único cliente
- Cliente valida autenticidade e integridade sem chamada adicional à nossa API
- HMAC-SHA256 tem suporte em biblioteca padrão em praticamente qualquer stack
- A rotação vira operação de rotina, sem janela de indisponibilidade

### Negativas

- Durante 24 horas convivem duas secrets válidas por endpoint, ampliando a janela de exposição de uma
  credencial comprometida — é o preço de não quebrar a integração do cliente
- Armazenamento e gestão de uma secret por endpoint, com o cuidado de nunca expô-la em log ou em
  resposta de leitura
- A verificação depende de o cliente implementá-la corretamente; a plataforma não tem como garantir que
  ele de fato confere a assinatura
- Uma secret perdida pelo cliente só se resolve por rotação, não por recuperação

## Referências

- Fatos: F-005, F-021, F-028, F-030
- Código: `src/shared/logger/index.ts` (redação de campos sensíveis em log),
  `src/middlewares/validate.middleware.ts` (validação da URL)
- ADRs: ADR-005 (headers de entrega), ADR-006 (reuso de padrões)
