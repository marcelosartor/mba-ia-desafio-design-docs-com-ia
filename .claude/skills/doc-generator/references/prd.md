# PRD — Product Requirement Document

**Altura:** produto e negócio. Responde *por que e o quê*.

Escrito por último entre os documentos grandes: com ADRs, RFC e FDD prontos, vira consolidação.

## Seções

Template em `assets/templates/PRD.md`.

1. **Resumo e contexto da feature**
2. **Problema e motivação** — a dor concreta, de quem, com evidência da fonte
3. **Público-alvo e cenários de uso**
4. **Objetivos e métricas de sucesso** — pelo menos um objetivo com **meta quantitativa**
5. **Escopo** — incluso e fora de escopo
6. **Requisitos funcionais** — `PRD-FR-NN`, um por linha, verificáveis
7. **Requisitos não funcionais** — `PRD-NFR-NN`, com números
8. **Decisões e trade-offs principais** — resumo com link para os ADRs, sem repetir o raciocínio deles
9. **Dependências**
10. **Riscos e mitigação** — `PRD-RISK-NN`, cada um com probabilidade, impacto e mitigação
11. **Critérios de aceitação** — objetivos; Gherkin (Dado/Quando/Então) quando ajuda a desambiguar
12. **Estratégia de testes e validação**

## Requisitos funcionais

Um requisito por item, no formato "o sistema deve permitir/garantir X". Cada um com ID e origem.
Requisito que não pode ser verificado por alguém de fora não é requisito, é intenção.

Não transformar detalhe de implementação em requisito funcional — "usa HMAC-SHA256" é decisão (ADR);
"o cliente consegue validar a autenticidade da notificação recebida" é requisito.

## Fora de escopo

Vem da **quarentena** do `facts.md` (`DESCARTADO` e `ADIADO`). Cada item com o motivo e a origem:

```markdown
- **Notificação por e-mail quando o endpoint falha repetidamente** — adiado para fase posterior,
  após medir o impacto da feature atual. Origem: [09:37] Larissa.
```

Distinguir "descartado" de "adiado": são coisas diferentes para quem lê planejando o roadmap.

## Métricas

Pelo menos uma meta numérica ancorada na fonte. Se a fonte dá o número ("abaixo de 10 segundos é tempo
real para eles"), ele vira meta. Se não dá, não inventar uma — marcar `[SEM FONTE]` e resolver com quem
tem a informação.

## Erros comuns

- Descer para detalhe técnico que pertence ao FDD.
- Listar como requisito algo que a reunião descartou.
- Métrica sem número ("melhorar a experiência de integração").
- Riscos sem mitigação, ou mitigação que é só "monitorar".
