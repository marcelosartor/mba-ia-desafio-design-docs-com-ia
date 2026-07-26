# Extração — transcrição e código

Fases F1 e F2. É aqui que se decide se o pacote inteiro será rastreável ou não.

## Transcrição

### Antes de escrever, classificar

Percorrer a transcrição inteira classificando cada trecho relevante. Não pular para a redação: a
tentação de "já sei o que a reunião decidiu" depois de ler metade é a origem mais comum de requisito
inventado.

| Classe | O que é | Vai para |
| --- | --- | --- |
| `DECISAO` | Decisão fechada, confirmada por alguém com papel para fechá-la | ADR, RFC, FDD |
| `RF` | Requisito funcional explícito | PRD, FDD |
| `RNF` | Meta de latência, tamanho, disponibilidade, segurança | PRD, FDD |
| `RESTRICAO` | Limite imposto (tecnologia, prazo, política) | PRD, RFC |
| `DESCARTADO` | Ideia colocada na mesa e rejeitada | Quarentena → Fora de escopo, Alternativas |
| `ADIADO` | Ideia aceita em mérito mas empurrada para outra fase | Quarentena → Fora de escopo |
| `ABERTO` | Levantado e não decidido | RFC → Questões em aberto |
| `GANCHO_CODIGO` | Menção a arquivo, classe, padrão existente | FDD → Integração |
| `RUIDO` | Saudação, oralidade, digressão | Descartado sem registro |

### Sinais linguísticos

- **Decisão fechada:** "tá decidido", "vamos registrar isso como decisão", "anotado", "fica assim",
  resumo final confirmado pelos participantes.
- **Descarte:** "não rola", "está fora de questão", "não dá", "descartamos", "é overengineering".
- **Adiamento:** "fica pra próxima fase", "agora não", "problema do futuro", "depois que a gente medir".
- **Em aberto:** "vale registrar como ponto em aberto", "a gente observa e decide depois",
  "por enquanto sim", "boa pergunta" seguido de nenhuma conclusão.

Atenção ao **resumo final** da reunião, quando existir: costuma confirmar o conjunto das decisões e é a
melhor âncora contra interpretação equivocada de um trecho isolado.

### Valores exatos

Extrair literalmente números, códigos, nomes de header, nomes de tabela e de classe. "5 tentativas",
"1m/5m/30m/2h/12h", "2 segundos", "64KB", "10 segundos", `X-Event-Id`, `WEBHOOK_*` — a paráfrase destrói
o valor do documento para quem vai implementar.

### Localização

Formato `[hh:mm] Nome`, copiado do trecho de origem. Se a transcrição não tiver timestamps, usar a
convenção que ela oferecer (número de linha, seção) e documentar essa escolha no manifesto.

### Registro

Um bloco por fato, no `facts.md`:

```
### F-NNN · <CLASSE>
Conteúdo: <uma linha, objetiva>
Fonte: TRANSCRICAO
Localização: [hh:mm] Nome
Citação: "<trecho literal, o suficiente para verificar>"
Consumido por: <IDs de documentos, preenchido conforme os docs são escritos>
```

Fatos relacionados ganham blocos distintos. Se um mesmo assunto foi discutido em vários momentos e
evoluiu, registrar o estado final como fato e os intermediários como contexto dentro da citação — o que
vale é onde a discussão chegou.

## Código

Objetivo: saber o que **realmente** existe, para que os documentos citem apenas isso.

### Roteiro

1. Estrutura: módulos, camadas, convenção de nomes de arquivo.
2. Ponto de integração da feature: onde o novo comportamento se conecta ao fluxo atual (o método, a
   transação, o middleware que será estendido) — abrir e ler, anotar linhas.
3. Padrões transversais reutilizáveis: erros, autenticação/autorização, logging, validação, resposta
   HTTP, configuração.
4. Modelo de dados e enums relevantes.
5. Entry-points e scripts, quando a feature adiciona um processo novo.

### Registro

`code-map.md`:

| Caminho | Verificado | O que é / gancho da feature |
| --- | --- | --- |
| `src/...` | sim | ... |

Anotar linhas quando o gancho é um trecho específico (`src/modules/orders/order.service.ts:126-179`).

**Sem trechos de código nos documentos finais** — caminho e linha bastam e não envelhecem tão rápido.

### Verificação

Todo caminho que entrar em `code-map.md` foi aberto nesta sessão. Antes de fechar a F2, conferir a lista
com `ls`/`Read`. O critério "nenhum arquivo mencionado é inexistente" é verificado pelo `validate.py`,
mas errar aqui custa uma rodada inteira de correção.
