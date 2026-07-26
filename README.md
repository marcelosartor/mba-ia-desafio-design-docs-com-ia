# Da Reunião ao Documento — pacote de design docs do Sistema de Webhooks

Entrega do desafio **"Da Reunião ao Documento: Design Docs Gerados por IA"** do MBA Arquitetura com IA.
O enunciado original está no [repositório base](https://github.com/devfullcycle/mba-ia-desafio-design-docs-com-ia).

## Sobre o desafio

O ponto de partida é uma transcrição literal de 55 minutos de reunião técnica em que cinco pessoas —
tech lead, PM, dois engenheiros e uma engenheira de segurança — decidem como construir um sistema de
webhooks de notificação de pedidos sobre um OMS já em produção. Nada foi registrado além da gravação.
A tarefa é transformar isso, junto com o código existente, em documentação acionável: PRD, RFC, FDD,
entre 5 e 8 ADRs, um tracker de rastreabilidade e este README.

A dificuldade real não é escrever os documentos: é **não escrever o que ninguém disse**. A reunião
descarta ideias, adia outras e deixa questões em aberto, e o modo de falha característico de um LLM é
justamente preencher esses vazios com o que "normalmente" existe em sistemas parecidos. Por isso a
entrega tem uma exigência de rastreabilidade total — cada item precisa apontar para um timestamp da
transcrição ou para um caminho de arquivo no repositório.

## Ferramentas de IA utilizadas

| Ferramenta | Papel exercido |
| --- | --- |
| **Claude Code (Opus)** | Ferramenta principal. Leu a transcrição e o código, extraiu e classificou os fatos, redigiu todos os documentos e executou o ciclo de validação e correção |
| **Skill `doc-generator`** (construída neste desafio) | Empacota o processo: pipeline em 10 fases, guias por documento, templates e o validador. Fica em [`.claude/skills/doc-generator/`](.claude/skills/doc-generator/) e é reutilizável em outros projetos |
| **Python (stdlib)** | O validador `validate.py` da skill — verifica seções, contagens, formato do tracker, existência dos caminhos citados e reaparecimento de itens descartados |

A decisão de construir uma skill em vez de escrever prompts avulsos veio da observação de que o desafio
tem duas camadas: produzir os documentos **e** produzir um processo que sobreviva ao desafio. A skill é
essa segunda camada.

## Workflow adotado

O trabalho foi organizado em dois blocos: **construir a skill** e depois **executá-la** sobre o desafio.

Antes de qualquer coisa, um `manifest.md` com todas as etapas, marcadas conforme concluídas, e um
`plano.md` acumulativo com o resultado de cada uma. Isso existe por um motivo prático: uma execução
longa pode ser interrompida por limite de contexto, e sem estado persistido o trabalho recomeça do zero.
De fato houve um reinício no meio do caminho — e a retomada custou minutos, não horas.

Para desenhar a skill, analisei dez conjuntos de prompts e plugins de geração de documentação já
existentes, incluindo os plugins do professor. O que cada um contribuiu está documentado na seção
"Origem do desenho" do [README da skill](.claude/skills/doc-generator/README.md).

A execução seguiu o pipeline da skill:

| Fase | Saída |
| --- | --- |
| F1 — Extração | `facts.md`: 40 fatos classificados, com citação literal e timestamp; 11 itens em quarentena; 4 questões em aberto |
| F2 — Mapa do código | `code-map.md`: caminhos abertos e verificados, com o gancho de cada um; arquivos propostos em seção separada |
| F3 — ADRs | 6 ADRs, um por decisão principal |
| F4 — RFC | Proposta técnica, alternativas descartadas e questões em aberto |
| F5 — FDD | Contratos, matriz de erros, fluxos, observabilidade e integração com o código |
| F6 — PRD | Consolidação de alto nível |
| F7 — Tracker | 74 itens rastreados |
| F8 — README | Este documento |
| F9 — Validação | `validate.py` até passar em todos os critérios |

A ordem **ADRs → RFC → FDD → PRD** não é arbitrária: as decisões formam o esqueleto do "como
implementar", e o PRD escrito por último vira consolidação em vez de adivinhação.

O ponto central do processo é a fase de extração. Nenhum documento lê a transcrição diretamente — todos
derivam do `facts.md`, em que cada fato já foi classificado como decisão, requisito, restrição,
descartado, adiado, questão em aberto ou gancho de código. Descartados e adiados vão para uma
**quarentena** que alimenta "Fora de escopo" e "Alternativas consideradas", e nunca vira requisito.

## Prompts customizados

### 1. Extração classificada com citação obrigatória (fase F1)

O prompt que substitui o "leia a transcrição e gere um PRD". A diferença está em exigir classificação
**antes** da redação e citação literal por fato:

```
Percorra TRANSCRICAO.md inteira e classifique cada trecho relevante em uma destas classes,
ANTES de redigir qualquer documento:

  DECISAO | RF | RNF | RESTRICAO | DESCARTADO | ADIADO | ABERTO | GANCHO_CODIGO | RUIDO

Para cada fato, produza um bloco:

  ### F-NNN · <CLASSE>
  Conteúdo: <uma linha objetiva>
  Fonte: TRANSCRICAO
  Localização: [hh:mm] Nome
  Citação: "<trecho literal, suficiente para verificar>"

Regras:
- Valores numéricos, códigos de erro e nomes de header vão LITERAIS. Nunca parafraseie
  "1m/5m/30m/2h/12h" como "intervalos crescentes".
- Sinais de decisão fechada: "tá decidido", "anotado", "vamos registrar". Sinais de descarte:
  "não rola", "está fora de questão", "é overengineering". Sinais de adiamento: "fica pra
  próxima fase", "problema do futuro".
- DESCARTADO e ADIADO vão para uma seção de QUARENTENA no fim do arquivo, com o motivo.
  Esses itens alimentam "Fora de escopo" e "Alternativas consideradas" e NUNCA viram requisito.
- Confira o resumo final da reunião antes de concluir: ele confirma o conjunto das decisões.
- Se você não consegue preencher Localização, o fato não existe. Não registre.
```

### 2. Seção de integração ancorada em código verificado (fase F5)

O que separa um FDD específico de um genérico. A regra de abrir o arquivo antes de citá-lo é o que
impede o caminho plausível-porém-inexistente:

```
Escreva a seção "Integração com o sistema existente" do FDD a partir de code-map.md.

Para CADA ponto de contato:
1. Abra o arquivo e leia o trecho relevante ANTES de escrever sobre ele.
2. Nomeie o caminho real e, quando o gancho for específico, as linhas.
3. Descreva o que o código faz HOJE e o que muda com a feature — não o que ele deveria fazer.
4. Sem trechos de código: caminho e linha bastam.

Arquivo que a feature vai CRIAR nunca aparece como existente. Ele vai para a tabela
"Arquivos novos propostos", com a palavra "proposto" explícita.

Ao terminar, rode validate.py: ele confere no disco todo caminho citado. Caminho inexistente
fora da tabela de propostos é falha de consistência, não detalhe de redação.
```

## Iterações e ajustes

### 1. `temp/desafio.md` vazio, execução iniciada com a fonte errada

A primeira execução partiu de um `desafio.md` de 0 byte. Em vez de parar, copiei o enunciado do
`README.md` e segui. Funcionou por acaso — o conteúdo era o mesmo — mas o processo estava
errado: começou sem validar a entrada mínima.

**Correção:** o processo foi zerado e reiniciado com o arquivo correto. A fase F0 da skill passou a
**abortar com `Status: ERRO`** quando falta entrada mínima, em vez de improvisar. Prosseguir "com o que
der" é exatamente como se produz documento sem lastro.

### 2. Caminho de arquivo citado como existente sendo proposta

O `validate.py` acusou que o ADR-002 citava `src/worker.ts` na seção de referências como se fosse código
atual. É um arquivo que a feature vai criar — a transcrição diz "criar um src/worker.ts", e o texto
absorveu isso como fato consumado. É precisamente o erro que destrói a confiança em um documento: o
leitor abre o caminho, não encontra nada, e passa a duvidar de todo o resto.

**Correção:** o ADR passou a marcar o arquivo como proposto, e o validador ganhou detecção de caminhos
declarados como propostos — no nível da seção e da linha — para distinguir proposta de alucinação sem
perder a verificação.

### 3. Nível de detalhe vazando entre documentos

A primeira versão do RFC trazia exemplo de payload e detalhe de headers. Isso é conteúdo do FDD: o RFC
responde "o que propomos e por quê", não "como construir". O sintoma clássico é gerar cada documento
isoladamente "completo", produzindo três documentos que dizem a mesma coisa em profundidades diferentes.

**Correção:** a regra de **altura** foi escrita explicitamente nos guias da skill, com uma tabela de
fronteira por documento e a orientação de referenciar em vez de copiar. O RFC ficou em nível de
arquitetura e aponta para o FDD.

### 4. Riscos sem consequência concreta

A primeira passagem produziu riscos do tipo "risco: indisponibilidade do cliente; mitigação: monitorar".
Tecnicamente verdadeiro, operacionalmente inútil.

**Correção:** exigência de probabilidade, impacto **concreto** e mitigação acionável — na maioria dos
casos, a mitigação já existia como decisão tomada (retry, DLQ, secret por endpoint) e bastava
referenciá-la. O item virou anti-padrão documentado na skill.

**Total: 4 ciclos principais** de geração, crítica e correção, além das rodadas menores conduzidas pelo
próprio validador até fechar em todos os critérios.

## Como navegar a entrega

| Ordem | Arquivo | Por que ler nesta posição |
| --- | --- | --- |
| 1 | [`docs/PRD.md`](docs/PRD.md) | Contexto de negócio: qual o problema, para quem, o que entra e o que ficou de fora |
| 2 | [`docs/RFC.md`](docs/RFC.md) | A proposta técnica em nível de arquitetura, com as alternativas descartadas e o que segue em aberto |
| 3 | [`docs/adrs/`](docs/adrs/) | As seis decisões, cada uma com seus trade-offs. Comece pelo ADR-001, que sustenta as demais |
| 4 | [`docs/FDD.md`](docs/FDD.md) | O detalhe de implementação: contratos, erros, fluxos e integração com o código atual |
| 5 | [`docs/TRACKER.md`](docs/TRACKER.md) | A verificação: de onde veio cada item dos documentos acima |
| 6 | [`.claude/skills/doc-generator/README.md`](.claude/skills/doc-generator/README.md) | Como o pacote foi produzido e como reaproveitar o processo em outro projeto |

Os ADRs, na ordem:

1. [ADR-001 — Padrão Outbox no MySQL](docs/adrs/ADR-001-outbox-no-mysql.md)
2. [ADR-002 — Worker em processo separado com polling](docs/adrs/ADR-002-worker-em-processo-separado-com-polling.md)
3. [ADR-003 — Retry com backoff e Dead Letter Queue](docs/adrs/ADR-003-retry-com-backoff-e-dead-letter-queue.md)
4. [ADR-004 — HMAC-SHA256 com secret por endpoint](docs/adrs/ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md)
5. [ADR-005 — Entrega at-least-once com `X-Event-Id`](docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md)
6. [ADR-006 — Reuso dos padrões existentes do projeto](docs/adrs/ADR-006-reuso-dos-padroes-existentes-do-projeto.md)

O código da aplicação (`src/`, `prisma/`, `tests/` e configurações) **não foi alterado** — a entrega é
puramente documental, e o código serviu como fonte de verdade.

### Reproduzindo a validação

```bash
python3 .claude/skills/doc-generator/scripts/validate.py \
  --profile .claude/skills/doc-generator/assets/profiles/mba-design-docs.json \
  --out docs --repo-root . --transcript TRANSCRICAO.md
```

O perfil usado no comando acima codifica os critérios de aceite do enunciado como regras verificáveis.
