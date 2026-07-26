# doc-generator

Skill do Claude Code que gera um **pacote de design docs rastreável** — PRD, RFC, FDD, ADRs, Tracker e
README de processo — a partir das fontes de verdade de um projeto: transcrição de reunião (opcional),
código-fonte e documentos existentes.

O diferencial não é gerar documento: é **não gerar documento sem lastro**. Cada requisito, decisão e
restrição carrega origem verificável. Quando a origem não existe, a skill marca `[SEM FONTE]` e o
validador falha — em vez de preencher a lacuna com o que "normalmente" existe em sistemas parecidos.

---

## Índice

- [Por que ela existe](#por-que-ela-existe)
- [Instalação](#instalação)
- [Uso](#uso)
- [Como funciona](#como-funciona)
- [Rastreabilidade](#rastreabilidade)
- [Perfis](#perfis)
- [Validador](#validador)
- [Estrutura de arquivos](#estrutura-de-arquivos)
- [Adaptando a outros projetos](#adaptando-a-outros-projetos)
- [Origem do desenho](#origem-do-desenho)
- [Limitações](#limitações)

---

## Por que ela existe

Documentação técnica gerada por IA falha de forma característica e previsível: inventa requisito
plausível, ressuscita ideia que a reunião descartou, cita arquivo que não existe, parafraseia número
exato e repete o mesmo conteúdo em três documentos com alturas diferentes.

A skill ataca cada um desses modos de falha com um mecanismo específico:

| Modo de falha | Mecanismo |
| --- | --- |
| Requisito inventado | Extração obrigatória para `facts.md` antes de qualquer redação |
| Descartado vira requisito | Quarentena separada + verificação cruzada no validador |
| Arquivo inexistente | `code-map.md` só com caminhos abertos e lidos; validador confere no disco |
| Número parafraseado | Regra de valores exatos com citação literal na extração |
| Documentos redundantes | Altura definida por documento; duplicação tratada como erro |
| "Passou de primeira" | Validador com critérios objetivos e ciclo de correção |

## Instalação

**No projeto** (a skill fica versionada junto com o repositório):

```bash
mkdir -p .claude/skills
cp -r <origem>/doc-generator .claude/skills/
```

**Global** (disponível em qualquer projeto do usuário):

```bash
cp -r <origem>/doc-generator ~/.claude/skills/
```

Requisitos: Claude Code e Python 3.8+ (o validador usa apenas a biblioteca padrão — sem `pip install`).

## Uso

A skill é acionada automaticamente por pedidos como *"gere os design docs dessa feature"*,
*"transforme essa transcrição em documentação técnica"*, *"crie os ADRs do projeto"*. Também pode ser
chamada explicitamente:

```
Use a skill doc-generator para documentar a feature X.
```

### Parâmetros

| Parâmetro | Padrão | Descrição |
| --- | --- | --- |
| `--sources` | inferido | `transcricao`, `codigo`, `docs` — o que existe como fonte |
| `--transcript` | procurado na raiz | Caminho da transcrição |
| `--code-root` | `src` | Raiz do código a mapear |
| `--profile` | `default` | Perfil de regras e limites |
| `--out` | `docs` | Destino dos documentos |
| `--work-dir` | `.doc-generator` | Estado e artefatos intermediários |
| `--docs` | todos | Subconjunto: `prd,rfc,fdd,adr,tracker,readme` |
| `--language` | `pt-BR` | Idioma dos documentos |
| `--phase` | primeira pendente | Retomar de uma fase específica |

### Exemplos

```
# pacote completo a partir de reunião + código
Use a skill doc-generator: --transcript=TRANSCRICAO.md --code-root=src --profile=default

# só ADRs, projeto sem transcrição (fonte = código)
Use a skill doc-generator: --sources=codigo --docs=adr

# retomar do FDD depois de uma interrupção
Use a skill doc-generator: --phase=F5
```

### Sem transcrição

A transcrição é **opcional**. Sem ela, a skill trabalha só com o código: os fatos passam a ter origem
`CODIGO`, os ADRs são derivados de decisões observáveis na base (estrutura, padrões, dependências) e o
tracker aponta para caminhos de arquivo. Perfis que exigem proporção mínima de linhas com origem em
transcrição devem ter `min_transcript_ratio` em `0` nesse cenário.

## Como funciona

Pipeline de 10 fases com estado persistido em `<work-dir>/MANIFEST.md`. Cada fase concluída é marcada
lá — se a execução parar no meio (limite de contexto, erro, interrupção), retoma-se da primeira fase
pendente sem refazer o que já está pronto.

| Fase | O que faz | Saída |
| --- | --- | --- |
| F0 | Valida entrada mínima, inicializa o manifesto | `MANIFEST.md` |
| F1 | Extrai e **classifica** os fatos da transcrição | `facts.md` |
| F2 | Mapeia o código, verificando cada caminho | `code-map.md` |
| F3 | Um ADR por decisão | `<out>/adrs/ADR-NNN-*.md` |
| F4 | RFC sobre as decisões registradas | `<out>/RFC.md` |
| F5 | FDD com contratos, erros e integração | `<out>/FDD.md` |
| F6 | PRD consolidando o alto nível | `<out>/PRD.md` |
| F7 | Tracker varrendo os documentos prontos | `<out>/TRACKER.md` |
| F8 | README do processo | `README.md` |
| F9 | Valida e corrige até passar | relatório |

A ordem é deliberada: **as decisões vêm primeiro** porque formam o esqueleto do "como implementar"; o
PRD vem por último porque, com ADRs, RFC e FDD prontos, ele é consolidação em vez de adivinhação.

### F1 — o coração anti-alucinação

Cada trecho da fonte é classificado **antes** de qualquer redação:

`DECISAO` · `RF` · `RNF` · `RESTRICAO` · `DESCARTADO` · `ADIADO` · `ABERTO` · `GANCHO_CODIGO` · `RUIDO`

`DESCARTADO` e `ADIADO` vão para a **quarentena**, que alimenta "Fora de escopo" (PRD) e "Alternativas
consideradas" (RFC) — e nunca vira requisito. O validador cruza a quarentena com a seção de requisitos e
acusa se um item ressuscitar.

Cada fato registrado carrega citação literal e localização:

```
### F-001 · DECISAO
Conteúdo: Outbox no MySQL, inserido na mesma transação da mudança de status.
Fonte: TRANSCRICAO
Localização: [09:06] Diego
Citação: "quando o status do pedido muda, dentro da mesma transação SQL (...) a gente também insere
uma linha numa tabela tipo webhook_outbox com o evento"
Consumido por: ADR-001, RFC, FDD
```

### Altura dos documentos

Duplicação entre documentos é tratada como erro, não como reforço:

| Documento | Responde | Altura |
| --- | --- | --- |
| PRD | Por que e o quê? | Produto / negócio |
| RFC | Como pretendemos resolver, e o que está aberto? | Arquitetura |
| ADR | Por que decidimos exatamente assim? | Decisão pontual |
| FDD | Como construir, em detalhe? | Implementação |
| Tracker | De onde veio cada coisa? | Transversal |

## Rastreabilidade

Todo item identificável recebe ID, e o ID aparece tanto no corpo do documento quanto no tracker:

| Prefixo | Item |
| --- | --- |
| `PRD-FR-NN` / `PRD-NFR-NN` | Requisito funcional / não funcional |
| `PRD-OUT-NN` / `PRD-RISK-NN` | Fora de escopo / risco |
| `RFC-ALT-NN` / `RFC-OPEN-NN` | Alternativa / questão em aberto |
| `FDD-FLUXO-NN` / `FDD-CONTRATO-NN` | Fluxo / contrato público |
| `FDD-ERRO-NN` / `FDD-INT-NN` | Linha da matriz de erros / ponto de integração |
| `ADR-NNN` | Decisão |

O tracker:

| ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização |
| --- | --- | --- | --- | --- | --- |
| PRD-FR-01 | docs/PRD.md | Requisito Funcional | Cadastro de endpoint com secret gerada pela plataforma | TRANSCRICAO | [09:31] Marcos |
| FDD-INT-01 | docs/FDD.md | Restrição | Evento publicado dentro da transação de mudança de status | CODIGO | src/modules/orders/order.service.ts |

**Regra de ouro:** se a coluna `Localização` não pode ser preenchida, o item não tem origem. Corrija ou
remova — nunca deduza a fonte.

## Perfis

Um perfil é um JSON que codifica as regras do pacote: seções obrigatórias por documento, contagens
mínimas, formato de nome de arquivo, limites e verificações globais. Trocar de contexto é trocar de
perfil, não editar a skill.

| Perfil | Uso |
| --- | --- |
| `default.json` | Projeto real genérico; limites moderados, sem exigência de transcrição |
| `mba-design-docs.json` | Desafio "Da Reunião ao Documento"; critérios de aceite do enunciado como regras |

### Criando um perfil

Copie `default.json` e ajuste. Campos principais:

```json
{
  "name": "meu-perfil",
  "error_code_prefix": "PAGAMENTO_",
  "documents": {
    "prd": { "path": "PRD.md", "sections": ["..."], "min_functional_requirements": 8 },
    "adr": { "dir": "adrs", "min_count": 5, "max_count": 8, "max_lines": 250 },
    "tracker": { "min_code_rows": 5, "min_transcript_ratio": 0.7, "min_id_coverage": 0.8 }
  },
  "global_checks": { "no_unsourced_markers": true, "verify_code_paths": true },
  "quarantine": ["ideia descartada na reunião"]
}
```

`sections` usa correspondência tolerante (sem acento, sem caixa, por substring), então
`"Critérios de aceite"` casa com `## 10. Critérios de aceite técnicos`.

## Validador

```bash
python3 scripts/validate.py \
  --profile assets/profiles/mba-design-docs.json \
  --out docs \
  --repo-root . \
  --transcript TRANSCRICAO.md
```

O que ele verifica:

1. Arquivos obrigatórios existem
2. Seções obrigatórias presentes em cada documento
3. Contagens mínimas: requisitos, ADRs, endpoints, alternativas, questões em aberto, riscos
4. ADRs: nomenclatura `ADR-NNN-kebab-case.md`, numeração sequencial sem lacunas, seções, tamanho
5. Prefixo dos códigos de erro na matriz do FDD
6. Tracker: formato da tabela, cobertura de IDs, proporção por fonte, `[hh:mm] Nome` válido **e presente
   na transcrição**, caminhos de código que existem no disco
7. Nenhum `[SEM FONTE]` remanescente
8. Nenhum item da quarentena aparecendo como requisito
9. Linguagem vaga proibida

Saída com `PASS`/`FAIL` por critério e código de saída diferente de zero em caso de falha — dá para usar
em CI.

```
## FDD
  [PASS] secao 'Contratos públicos'
  [FAIL] >= 4 caminhos reais na integracao — 2 de 5 existem
  [PASS] observabilidade cita 'tracing'

------------------------------------------------------------
78/82 criterios OK
```

Rode ao fim de cada fase de redação, não só no final: corrigir cedo custa uma fração.

## Estrutura de arquivos

```
doc-generator/
├── SKILL.md                     # ponto de entrada; regras e pipeline
├── README.md                    # este arquivo
├── references/
│   ├── workflow.md              # as 10 fases em detalhe + protocolo de retomada
│   ├── extraction.md            # transcrição→fatos e código→mapa
│   ├── adr.md                   # guia e limites do ADR
│   ├── rfc.md                   # guia do RFC e fronteira com o FDD
│   ├── fdd.md                   # guia do FDD
│   ├── prd.md                   # guia do PRD
│   ├── tracker.md               # esquema de IDs e regras de cobertura
│   ├── process-readme.md        # guia do README de processo
│   └── anti-patterns.md         # 12 modos de falha e correções
├── assets/
│   ├── templates/               # MANIFEST, facts, code-map, ADR, RFC, FDD, PRD, TRACKER, README
│   └── profiles/                # default.json, mba-design-docs.json
└── scripts/
    └── validate.py              # validador (stdlib)
```

Os guias são carregados sob demanda, por fase — o `SKILL.md` fica enxuto e o contexto só recebe o que a
fase corrente precisa.

## Adaptando a outros projetos

A skill foi construída para não ficar presa ao caso que a originou.

**Outro domínio.** Nada nos guias assume webhooks, Node ou MySQL. O `error_code_prefix` do perfil ajusta
o padrão de códigos de erro; `code-root` aponta para a raiz do código, qualquer que seja a linguagem.

**Sem reunião.** Use `--sources=codigo`. Os fatos passam a ter origem `CODIGO` e os ADRs derivam de
decisões observáveis na base.

**Outro conjunto de documentos.** `--docs=adr,tracker` gera só o que interessa. O perfil declara quais
documentos são obrigatórios.

**Outro idioma.** `--language`. Convenção herdada dos plugins de referência: traduzem-se cabeçalhos,
status e texto corrido; mantêm-se em inglês nomes de tecnologia, identificadores técnicos, códigos de
erro e caminhos de arquivo.

**Outra régua de qualidade.** É a razão de os perfis serem JSON: a régua de um time não vira fork da
skill.

## Origem do desenho

A skill consolida padrões extraídos de dez conjuntos de prompts e plugins de geração de documentação:

| Padrão herdado | Origem |
| --- | --- |
| Pipeline em fases com manifesto como fonte de verdade e retomada | `AgenteGeradorDeDocumentos-SAD-DPR` |
| Rastreabilidade por ID (`CU-XX`/`RNF-XX`/`DEC-XX`) e regra de não fabricação | `AgenteGeradorDeDocumentos-SAD-DPR` |
| Etapas sequenciais com gate e categoria "não verificável" | `ConferenciaDePeticoes` |
| Varre fonte → inventário → um arquivo por item | `DocimentarLibsExternasDeProjectosViaContext7` |
| Iteração com critério de parada por cobertura estrutural medida | `EnriquecimentoDePetições` |
| Esqueleto de FDD/HLD, contratos com exemplo, riscos com probabilidade/impacto | `FDD-HLD` |
| MADR estrito, limites numéricos, `[NECESSITA INPUT]`, 1 ADR = 1 Task paralela | `GeradoresDeDocumentos` (marketplace Full Cycle) |
| Política de tradução parcial e parametrização por `--language` | `GeradoresDeDocumentosPtBr` |
| Leitura de transcrição descartando oralidade; marcação de conteúdo derivado | `Resumos` |
| Seção nominal "FONTE DA VERDADE" e proibição de alterar o original | `TradudorDeProjetosPtBr` |
| Raciocínio explícito antes de redigir; extração de valores exatos; Gherkin | `UserStoriesBugs` |

O marcador de lacuna aparecia com nomes diferentes em quase todos eles — `lacuna`,
`[NECESSITA INPUT]`, `NÃO VERIFICÁVEL`, `[exemplo inferido]`. Aqui virou `[SEM FONTE]`, com uma
diferença: é **bloqueante**, não decorativo.

## Limitações

- **Qualidade limitada pela fonte.** Reunião vaga produz documento vago. A skill impede invenção, não
  cria informação que não foi dita nem existe no código.
- **Classificação de fala é interpretativa.** "Fica pra próxima fase" é adiamento claro; nem tudo é.
  A quarentena deve ser revisada por quem participou.
- **O validador verifica forma, não verdade.** Ele confirma que existe uma seção "Observabilidade" com
  as três palavras, não que as métricas propostas façam sentido. Revisão humana continua necessária.
- **Cobertura de IDs é heurística.** Conta IDs no padrão declarado; item registrado sem ID escapa da
  medição.
- **Paralelismo de ADRs depende do ambiente.** O padrão "1 ADR = 1 Task" pressupõe subagentes
  disponíveis e autorizados; sem eles a execução é sequencial, com a mesma exigência de cobertura 1:1.
