# ADR — Architecture Decision Record

**Altura:** uma decisão isolada. Responde *por que decidimos exatamente assim*.

Um ADR não descreve a solução inteira nem ensina a implementar. Ele registra uma escolha, as opções que
perderam e o preço que se aceitou pagar.

## Regras

- **1 decisão = 1 arquivo.** Mudou? Edite o existente; não crie um segundo.
- Nome: `ADR-NNN-titulo-em-kebab-case.md`, sem acentos, numeração sequencial sem lacunas.
- **100–250 linhas.** ADR de 600 linhas virou FDD.
- **Máximo 3 opções** consideradas. Se só havia duas razoáveis, dizer por que não houve terceira.
- **Máximo 5 referências de arquivo.** Caminho (e linha), nunca trecho de código.
- Toda afirmação ancorada em `F-NNN` do `facts.md`.
- Pelo menos uma consequência **negativa** explícita. ADR só com benefícios é propaganda.
- Sem sugestão de trabalho futuro ("considere avaliar X"), sem detalhe de implementação
  (nomes de variável, cron, config), sem emoji.

## Seções

Estrutura MADR. Template em `assets/templates/ADR.md`.

```markdown
# ADR-NNN: <Título>

**Status:** Aceito | Proposto | Rejeitado | Obsoleto | Substituído por ADR-NNN
**Data:** YYYY-MM-DD
**ADRs Relacionados:** ADR-NNN (opcional)

## Contexto

## Drivers da Decisão

## Decisão

## Alternativas Consideradas

## Consequências

### Positivas
### Negativas

## Referências
```

### Contexto
Dois a quatro parágrafos: qual o problema, quais forças atuam (restrições, RNFs, prazo, tamanho do
time), por que decidir agora. Referenciar os fatos de origem.

### Drivers da Decisão
Lista curta do que realmente pesou. São os critérios contra os quais as alternativas foram avaliadas —
se um driver não é usado para separar opções, ele não é driver.

### Decisão
Declarativa, no presente. "Adotamos X." Seguida da justificativa contra os drivers.

### Alternativas Consideradas
Cada alternativa com **o trade-off que motivou o descarte** — não basta listar o nome. Alternativas
vindas da quarentena (`DESCARTADO` em `facts.md`) são as mais valiosas: foram discutidas de verdade.

### Consequências
Positivas e negativas. As negativas são o trade-off aceito, e precisam ser específicas: "perde garantia
de ordenação global se escalar para múltiplos workers" vale; "pode ter alguma complexidade" não vale.

### Referências
`F-NNN` de origem, caminhos de código relevantes, ADRs relacionados.

## Lacunas

Falta um dado para fechar a decisão (uma meta de SLA, um custo)? Marcar `[SEM FONTE]` no ponto exato e
resolver antes da entrega — o validador falha enquanto houver marcador.

Máximo de 4 marcadores por ADR; acima disso, a decisão não está madura o bastante para virar ADR.
