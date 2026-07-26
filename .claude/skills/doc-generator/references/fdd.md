# FDD — Feature Design Document

**Altura:** implementação. Responde *como construir, em detalhe*.

Critério de pronto: um desenvolvedor que não participou da discussão consegue começar a codar sem
perguntar nada essencial.

## Seções

Template em `assets/templates/FDD.md`.

1. **Contexto e motivação técnica** — o problema técnico, como a feature se encaixa no que existe,
   atores e limites.
2. **Objetivos técnicos** — cada um com medida ou invariante verificável.
3. **Escopo e exclusões** — incluído e explicitamente fora.
4. **Fluxos detalhados** — principal e variações, passo a passo. Onde valida, onde persiste, onde chama
   fora, o que acontece em falha. Diagrama (Mermaid) quando o fluxo tem ramificação relevante.
5. **Contratos públicos** — endpoints/assinaturas com **exemplo de requisição e de resposta**, headers e
   sua semântica, status codes e o que cada um significa, limites (tamanho, timeout, taxa).
6. **Matriz de erros** — tabela com código, condição, status HTTP e tratamento. Códigos seguem o padrão
   já existente no projeto (prefixo por módulo).
7. **Estratégias de resiliência** — timeouts, retries, backoff, fallback, circuit breaker. **Com os
   números da fonte**, não com adjetivos.
8. **Observabilidade** — métricas (nome e o que cada uma responde), logs (campos estruturados, o que
   nunca pode ser logado), tracing (spans e propagação). As três, sempre.
9. **Dependências e compatibilidade** — o que precisa existir, versões mínimas, impacto em interfaces
   atuais.
10. **Critérios de aceite técnicos** — checklist objetivo, verificável, com metas numéricas.
11. **Riscos e mitigação** — probabilidade, impacto, mitigação, contingência.
12. **Integração com o sistema existente** — ver abaixo.

## Integração com o sistema existente

A seção que separa um FDD real de um FDD genérico. Vem de `code-map.md`.

Para cada ponto de contato, nomear o **caminho real do arquivo** e descrever concretamente o que muda:

```markdown
### `src/modules/orders/order.service.ts`

O método `changeStatus` (l. 126–179) executa hoje, na mesma transação, a validação da transição, o
ajuste de estoque, o `update` da ordem e a inserção no histórico. A publicação do evento entra **dentro
desta transação**, após a inserção no histórico: se ela falhar, a mudança de status faz rollback junto.
```

Mínimo: os pontos de extensão de fluxo, os padrões reutilizados (erros, auth, log, validação) e o
modelo de dados.

**Toda referência aqui é verificada.** Arquivo inexistente citado é falha de consistência — e é o tipo
de erro que destrói a confiança no documento inteiro.

## Rastreabilidade

`FDD-CONTRATO-NN` para cada contrato público, `FDD-ERRO-NN` para cada linha da matriz de erros,
`FDD-INT-NN` para cada ponto de integração, `FDD-FLUXO-NN` para cada fluxo.

## Erros comuns

- Contrato sem exemplo de payload. Exemplo é o que torna o contrato acionável.
- Matriz de erros com códigos inventados, fora do padrão do projeto.
- Observabilidade genérica ("logar erros"). Nomear métrica, campo e span.
- Repetir a justificativa das decisões — isso é dos ADRs; aqui só o link.
- Números arredondados "para ficar redondo" quando a fonte dá o valor exato.
