# Workflow — as 10 fases

Estado em `<work-dir>/MANIFEST.md`. Nenhuma fase começa sem que a anterior esteja marcada como concluída
nele. Isso é o que permite retomar depois de uma interrupção.

## Protocolo de retomada

1. Ler `<work-dir>/MANIFEST.md`.
2. Achar a primeira fase `[ ]`.
3. Ler os artefatos das fases anteriores (`facts.md`, `code-map.md`, documentos já escritos).
4. Continuar dali. Não regerar o que já está pronto e registrado.

Ao concluir uma fase: gravar o artefato → marcar `[x]` no manifesto → anexar linha no log com data e
observação. Nessa ordem.

---

## F0 — Setup e validação de entrada

**Entrada mínima:** pelo menos uma fonte legível (código **ou** transcrição) e um destino de saída.

Verificar e registrar no manifesto:
- Fontes encontradas e seus caminhos
- Perfil em uso e limites que ele impõe
- Lista de documentos a produzir
- Work-dir e destino

Se faltar entrada mínima, **abortar** com:

```
Status: ERRO
Motivo: <o que falta, especificamente>
Próximos passos: <o que o usuário precisa fornecer>
```

Não prosseguir "com o que der". Documento sem fonte é o problema que esta skill existe para evitar.

Criar `<work-dir>/MANIFEST.md` a partir de `assets/templates/MANIFEST.md`.

---

## F1 — Extração de fatos

Só roda se houver transcrição. Sem ela, `facts.md` é gerado apenas com fatos de origem `CODIGO` na F2.

Ler `references/extraction.md`. Produzir `<work-dir>/facts.md` com um registro por fato:

```
### F-001 · DECISAO
Conteúdo: Outbox no MySQL, inserido na mesma transação da mudança de status.
Fonte: TRANSCRICAO
Localização: [09:06] Diego
Citação: "quando o status do pedido muda, dentro da mesma transação SQL (...) a gente também insere
uma linha numa tabela tipo webhook_outbox com o evento"
Consumido por: ADR-001, RFC, FDD
```

Classificação obrigatória de cada fato — feita **antes** de qualquer redação:

`DECISAO` · `RF` · `RNF` · `RESTRICAO` · `DESCARTADO` · `ADIADO` · `ABERTO` · `GANCHO_CODIGO` · `RUIDO`

`RUIDO` (saudações, oralidade, digressão) é descartado sem registro.

**Quarentena:** `DESCARTADO` e `ADIADO` ficam em seção própria no fim do `facts.md`. Alimentam
"Fora de escopo" (PRD) e "Alternativas consideradas" (RFC). Nunca viram requisito — o validador cruza
a quarentena com o corpo dos documentos e acusa reaparecimento.

---

## F2 — Mapa do código

Produzir `<work-dir>/code-map.md`: tabela de caminhos **verificados** com o gancho de cada um para a
feature. Ver `references/extraction.md`, seção "Código".

Todo caminho aqui foi aberto e lido. Caminho plausível mas não verificado é alucinação com formatação
melhor.

---

## F3 — ADRs

Uma decisão (`DECISAO` em `facts.md`) = um ADR = um arquivo. Ler `references/adr.md`.

Em contexto com subagentes disponíveis e autorizados, o padrão é uma `Task` por ADR, em paralelo, e o
coordenador confere linha a linha se todo `DECISAO` virou arquivo. Sem subagentes, sequencial — o
requisito de cobertura 1:1 não muda.

Numeração sequencial sem lacunas, `ADR-NNN-titulo-em-kebab-case.md`.

---

## F4 — RFC

Ler `references/rfc.md`. Consome `facts.md` (quarentena → alternativas descartadas; `ABERTO` → questões
em aberto) e referencia os ADRs da F3 por link.

Conciso. Se estiver detalhando implementação, o conteúdo pertence ao FDD.

---

## F5 — FDD

Ler `references/fdd.md`. Consome `code-map.md` para a seção de integração com o sistema existente.

É o documento mais longo e mais concreto: contratos com exemplo, matriz de erros, resiliência com
números, observabilidade.

---

## F6 — PRD

Ler `references/prd.md`. Com ADRs, RFC e FDD prontos, o PRD é consolidação de alto nível — não é o
lugar de detalhe técnico.

---

## F7 — Tracker

Ler `references/tracker.md`. Varre os documentos prontos e monta a tabela de rastreabilidade.

Regra de ouro: linha cuja coluna `Localização` não pode ser preenchida indica item sem origem — voltar
ao documento e corrigir ou remover o item, não inventar a fonte.

---

## F8 — README de processo

Ler `references/process-readme.md`. Descreve a jornada real: ferramentas, ordem, prompts usados e o que
precisou ser corrigido. Escrever no fim, quando há o que contar.

---

## F9 — Validação e correção

```bash
python3 scripts/validate.py --profile <perfil.json> --out <out> --repo-root . [--transcript <caminho>]
```

Para cada `FAIL`: corrigir o documento e rodar de novo. Repetir até verde.

Depois do verde automático, revisão manual do que o script não alcança:
- Algum documento repete o que outro já diz? (violação de altura)
- Alguma frase é vaga a ponto de não significar nada?
- Algum número foi parafraseado em vez de citado?
- Algum item da quarentena voltou disfarçado de requisito?
