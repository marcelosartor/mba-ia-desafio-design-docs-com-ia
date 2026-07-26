# Anti-padrões

Os modos de falha recorrentes na geração de design docs por IA, e o que fazer no lugar.

## 1. Requisito sem origem

**Sintoma:** o documento afirma algo plausível que ninguém disse e o código não mostra.
**Por que acontece:** o modelo completa lacunas com o que "normalmente" existe nesse tipo de sistema.
**Correção:** todo item passa pelo `facts.md`. Sem `F-NNN`, não entra. Na dúvida, `[SEM FONTE]`.

## 2. Descartado que volta como requisito

**Sintoma:** o PRD lista uma funcionalidade que a reunião rejeitou explicitamente.
**Por que acontece:** o trecho foi lido como "ideia mencionada" sem registrar o veredito.
**Correção:** quarentena separada em `facts.md`; validador cruza quarentena contra o corpo dos docs.

## 3. Caminho de arquivo inventado

**Sintoma:** o FDD cita `src/modules/webhooks/webhook.service.ts` — que ainda não existe — como se fosse
código atual.
**Por que acontece:** extrapolação do padrão de nomes do projeto.
**Correção:** `code-map.md` só com caminhos abertos e lidos. Arquivo **proposto** pela feature é sempre
marcado como proposto, nunca como existente.

## 4. Documentos que se repetem

**Sintoma:** o RFC tem a matriz de erros; o FDD reexplica por que se escolheu a abordagem; o PRD desce a
headers HTTP.
**Por que acontece:** cada documento é gerado "completo" isoladamente.
**Correção:** respeitar a altura. Ao escrever, perguntar: outro documento do pacote já responde isso?
Se sim, link, não cópia.

## 5. Número parafraseado

**Sintoma:** "retries com intervalos crescentes" onde a fonte diz "1m, 5m, 30m, 2h, 12h".
**Correção:** valores exatos, sempre. A paráfrase apaga exatamente a informação que o implementador
precisa.

## 6. Alternativa decorativa

**Sintoma:** "Alternativas consideradas: A, B, C" sem dizer por que B e C perderam.
**Correção:** alternativa sem trade-off de descarte não entra. Melhor duas alternativas reais do que
três com uma inventada.

## 7. ADR inchado

**Sintoma:** 600 linhas, com implementação, monitoramento e trabalho futuro.
**Correção:** 100–250 linhas, 7 seções, foco na decisão. Implementação é do FDD.

## 8. Observabilidade genérica

**Sintoma:** "logar erros e monitorar a fila".
**Correção:** nome da métrica e o que ela responde; campos estruturados do log e o que nunca pode ser
logado; spans e propagação.

## 9. Risco sem consequência

**Sintoma:** "Risco: indisponibilidade do cliente. Mitigação: monitorar."
**Correção:** probabilidade, impacto concreto e mitigação acionável — que costuma já existir como
decisão (retry, DLQ) e pode ser referenciada.

## 10. Tracker preenchido no fim, de memória

**Sintoma:** localizações aproximadas, timestamps que não batem com a transcrição.
**Correção:** copiar `Fonte` e `Localização` do `facts.md`/`code-map.md`. Se der trabalho, é sinal de
que o item foi escrito sem consultar a fonte.

## 11. Linguagem vaga

Evitar: "provavelmente escalável", "deve atender bem", "robusto", "moderno", "melhor prática do
mercado". Se a afirmação não pode ser verificada, ou vira número, ou sai.

## 12. Passar de primeira

Pacote gerado em uma rodada, sem nenhuma correção, quase sempre está genérico. Rodar o validador, ler
criticamente, corrigir. Três a cinco ciclos é o normal.
