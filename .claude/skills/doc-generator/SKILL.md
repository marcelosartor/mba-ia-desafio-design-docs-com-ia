---
name: doc-generator
description: Gera um pacote de design docs rastreável (PRD, RFC, FDD, ADRs, Tracker e README de processo) a partir das fontes de verdade de um projeto — transcrição de reunião (opcional), código-fonte e documentos existentes. Todo item registrado carrega origem verificável; nada é inventado. Use quando o usuário pedir para documentar uma feature, transformar uma reunião em documentação técnica, gerar ADRs/RFC/FDD/PRD, criar rastreabilidade entre documentos e código, ou montar documentação de design a partir de transcrição. Aciona com pedidos como "gere os design docs", "documente essa feature", "transforme essa transcrição em documentação", "crie os ADRs do projeto".
---

# doc-generator

Produz um pacote de design docs em que **cada afirmação tem origem rastreável** na transcrição ou no
código. A skill não escreve sobre o que não conseguiu ancorar: quando falta fonte, marca `[SEM FONTE]`
e o validador falha.

## Fonte da verdade

| Entrada | Obrigatória | Papel |
| --- | --- | --- |
| Código-fonte | Sim | Padrões existentes, pontos de integração, restrições reais |
| Transcrição de reunião | Não | Decisões, requisitos, descartes, adiamentos, questões em aberto |
| Documentos existentes (`docs/`) | Não | Convenções e material já produzido |

As fontes são **read-only**. A skill escreve apenas em `--out` (padrão `docs/`), no `README.md` de
processo e no work-dir.

## Regras invioláveis

1. **Zero fabricação.** Sem fonte identificável, o item não entra. Se for indispensável, entra marcado
   `[SEM FONTE]` — que o validador trata como erro bloqueante.
2. **Extração antes de redação.** Nenhum documento é escrito antes de `facts.md` e `code-map.md`
   existirem. Documentos derivam dos fatos, não da fonte crua.
3. **Descartado é descartado.** O que a reunião rejeitou ou adiou vai para a quarentena e alimenta
   "Fora de escopo". Nunca vira requisito.
4. **Altura de documento.** PRD = por quê/o quê · RFC = como propomos e o que está aberto ·
   ADR = por que decidimos assim · FDD = como construir · Tracker = de onde veio.
   Conteúdo duplicado entre documentos é erro, não redundância útil.
5. **Caminho citado é caminho verificado.** Todo arquivo mencionado em qualquer documento existe no
   repositório — conferir com `ls`/`Read` antes de escrever.
6. **Valores exatos.** Números, códigos de erro, headers e nomes vêm literais da fonte. Nunca parafrasear
   "2 segundos" como "poucos segundos".
7. **Um artefato por unidade de decisão.** 1 ADR = 1 arquivo. Mudou? Edite o existente, não crie outro.
8. **Sem emojis, sem estimativa de esforço não fundamentada, sem linguagem vaga**
   ("provavelmente escalável", "deve atender").

## Invocação

```
--sources=transcricao,codigo,docs   # o que existe como fonte
--transcript=<caminho>              # ex.: TRANSCRICAO.md
--code-root=src                     # raiz do código a mapear
--profile=default|<caminho.json>    # regras e limites do pacote
--out=docs                          # destino dos documentos
--work-dir=.doc-generator           # estado e artefatos intermediários
--docs=prd,rfc,fdd,adr,tracker,readme
--language=pt-BR
--phase=F0..F9                      # retomar de uma fase específica
```

Sem argumentos: inferir do repositório (procurar transcrição na raiz, usar `src/` e `docs/`), confirmar
o que foi inferido e seguir com o perfil `default`.

## Pipeline

Estado em `<work-dir>/MANIFEST.md`. Cada fase concluída é registrada nele — a execução é **retomável**.

| Fase | O que faz | Saída |
| --- | --- | --- |
| F0 | Valida entrada mínima e inicializa o manifesto | `MANIFEST.md` |
| F1 | Extrai fatos da transcrição, classificados e com citação | `facts.md` |
| F2 | Mapeia o código: caminhos verificados e ganchos | `code-map.md` |
| F3 | Um ADR por decisão | `<out>/adrs/ADR-NNN-*.md` |
| F4 | RFC sobre as decisões já registradas | `<out>/RFC.md` |
| F5 | FDD detalhando implementação | `<out>/FDD.md` |
| F6 | PRD consolidando o alto nível | `<out>/PRD.md` |
| F7 | Tracker varrendo os documentos prontos | `<out>/TRACKER.md` |
| F8 | README do processo | `README.md` |
| F9 | Valida e corrige até passar | relatório |

Ordem deliberada: as decisões formam o esqueleto; o PRD por último vira consolidação.

**Antes de iniciar, leia `references/workflow.md`** — contém o detalhamento de cada fase, o formato do
manifesto e o protocolo de retomada.

## Guias por documento

Carregue o guia da fase corrente, não todos de uma vez:

| Fase | Guia |
| --- | --- |
| F1–F2 | `references/extraction.md` |
| F3 | `references/adr.md` |
| F4 | `references/rfc.md` |
| F5 | `references/fdd.md` |
| F6 | `references/prd.md` |
| F7 | `references/tracker.md` |
| F8 | `references/process-readme.md` |
| qualquer | `references/anti-patterns.md` |

Templates em `assets/templates/`. Perfis em `assets/profiles/`.

## Validação

```bash
python3 scripts/validate.py --profile <perfil.json> --out docs --repo-root . [--transcript TRANSCRICAO.md]
```

Só stdlib. Reporta `PASS`/`FAIL` por critério e sai com código diferente de zero se algo falhar.
Rode ao fim de cada fase de redação, não apenas no final — corrigir cedo custa menos.

**Expectativa realista:** 3 a 5 ciclos de geração → crítica → correção. Documentos que passam de primeira
costumam estar genéricos demais.
