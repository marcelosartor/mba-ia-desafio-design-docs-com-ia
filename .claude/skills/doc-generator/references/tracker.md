# Tracker de rastreabilidade

**Altura:** transversal. Responde *de onde veio cada coisa*.

É a defesa contra alucinação. Se a coluna `Localização` não pode ser preenchida para um item, aquele
item não tem origem — corrija ou remova do documento. Nunca preencha a fonte "por dedução".

## Formato

```markdown
| ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização |
| --- | --- | --- | --- | --- | --- |
| PRD-FR-01 | docs/PRD.md | Requisito Funcional | Cadastro de endpoint de webhook com secret gerada pela plataforma | TRANSCRICAO | [09:31] Marcos |
| FDD-INT-01 | docs/FDD.md | Restrição | Evento publicado dentro da transação de mudança de status | CODIGO | src/modules/orders/order.service.ts |
```

- **ID** — único, no esquema do documento de origem
- **Documento** — caminho do arquivo onde o item aparece
- **Tipo** — Requisito Funcional, Requisito Não Funcional, Decisão, Restrição, Trade-off, Alternativa,
  Questão em Aberto, Contrato, Erro, Risco
- **Conteúdo (resumo)** — uma linha; o suficiente para reconhecer o item sem abrir o documento
- **Fonte** — `TRANSCRICAO` ou `CODIGO`
- **Localização** — `[hh:mm] Nome` para transcrição; caminho de arquivo real para código

## Esquema de IDs

| Prefixo | Item |
| --- | --- |
| `PRD-FR-NN` | Requisito funcional |
| `PRD-NFR-NN` | Requisito não funcional |
| `PRD-OUT-NN` | Item fora de escopo |
| `PRD-RISK-NN` | Risco |
| `RFC-ALT-NN` | Alternativa considerada |
| `RFC-OPEN-NN` | Questão em aberto |
| `FDD-FLUXO-NN` | Fluxo |
| `FDD-CONTRATO-NN` | Contrato público |
| `FDD-ERRO-NN` | Linha da matriz de erros |
| `FDD-INT-NN` | Ponto de integração com o código |
| `ADR-NNN` | Decisão |

Use o mesmo ID no corpo do documento e na tabela, para a referência cruzada funcionar nos dois sentidos.

## Como montar

1. Varrer os documentos prontos, extraindo cada item identificável.
2. Para cada um, localizar o fato de origem em `facts.md` ou a entrada em `code-map.md`.
3. Copiar `Fonte` e `Localização` de lá — nunca reescrever de memória.
4. Item sem origem: voltar ao documento. Ou o item sai, ou a fonte aparece.

## Cobertura

O perfil define os mínimos (tipicamente: ≥80% dos itens identificáveis na tabela, proporção mínima de
linhas com origem em transcrição, número mínimo de linhas com origem em código). O `validate.py` mede.

Cobertura não é sobre encher a tabela: é sobre não deixar item importante sem lastro. Uma tabela com
200 linhas triviais e sem os requisitos principais falha o objetivo mesmo passando no número.

## Verificação

- Todo caminho na coluna `Localização` com fonte `CODIGO` existe no repositório.
- Todo `[hh:mm] Nome` com fonte `TRANSCRICAO` aparece na transcrição, com esse nome.
- Todo ID citado no corpo dos documentos tem linha correspondente.
