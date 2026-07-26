# RFC — Request for Comments

**Altura:** arquitetura. Responde *como pretendemos resolver, e o que ainda está em aberto*.

É um documento submetido à equipe para revisão. Fala em decisão e em dúvida — não em implementação.
Conciso: 2 a 4 páginas.

## Fronteira com os outros documentos

| Pergunta | Documento |
| --- | --- |
| Por que estamos fazendo isso? | PRD |
| Qual a abordagem e o que ainda não sabemos? | **RFC** |
| Por que decidimos exatamente assim? | ADR |
| Como construir? | FDD |

Se o RFC estiver com exemplo de payload, matriz de erro ou assinatura de função, o conteúdo é do FDD.
Se estiver dissecando uma decisão isolada com prós e contras longos, é do ADR — aqui basta o link.

## Seções

Template em `assets/templates/RFC.md`.

1. **Metadados** — autor, status, data, revisores. Revisores são pessoas reais envolvidas na discussão;
   quando a fonte é uma reunião, são os participantes, com seus papéis.
2. **Resumo executivo (TL;DR)** — a proposta inteira em um parágrafo. Quem ler só isso precisa entender
   o que muda.
3. **Contexto e problema** — o que existe hoje, o que dói, o que motiva mexer agora.
4. **Proposta técnica** — visão geral da solução: componentes, fluxo em alto nível, garantias oferecidas.
   Nível de detalhe: suficiente para revisar a abordagem, não para implementá-la.
5. **Alternativas consideradas** — pelo menos as que foram realmente discutidas e descartadas, **cada uma
   com o trade-off que motivou o descarte**. Vêm da quarentena do `facts.md`. Alternativa sem motivo de
   descarte não é alternativa, é lista.
6. **Questões em aberto** — o que foi levantado e não decidido, ou adiado conscientemente. Esta seção é o
   ponto do documento: um RFC sem dúvidas não precisa de revisão.
7. **Impacto e riscos** — o que quebra, o que fica mais lento, o que exige coordenação com terceiros.
8. **Decisões relacionadas** — links para os ADRs correspondentes, com o título de cada um.

## Rastreabilidade

Cada alternativa recebe `RFC-ALT-NN`; cada questão em aberto, `RFC-OPEN-NN`. Esses IDs entram no tracker
com a origem correspondente.

## Erros comuns

- Repetir o FDD em versão resumida — o RFC não é sumário do FDD, é o documento que veio antes.
- Listar como "aberto" algo que a reunião fechou (leia o resumo final antes de concluir).
- Apresentar alternativa fictícia "para parecer completo". Se só houve duas na mesa, são duas.
- Prometer no RFC número que não foi decidido em lugar nenhum.
