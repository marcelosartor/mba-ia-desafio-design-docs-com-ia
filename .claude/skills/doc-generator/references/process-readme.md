# README de processo

Documenta **como o pacote foi produzido** — não o que ele contém (isso é dos documentos) nem o que o
projeto faz (isso é do README do projeto, quando são arquivos diferentes).

Escrito por último, quando existe processo real para contar.

## Seções

Template em `assets/templates/README-processo.md`.

1. **Sobre o desafio / o trabalho** — 1 a 2 parágrafos, em palavras próprias, sobre o que foi pedido.
2. **Ferramentas de IA utilizadas** — cada uma com o papel que exerceu. Não é lista de logos: "usei X
   para varrer o código e Y para revisar o tracker" diz algo; "usei X, Y e Z" não.
3. **Workflow adotado** — em que ordem os documentos foram produzidos e por quê; como a interação foi
   organizada; onde ficou o estado.
4. **Prompts customizados** — pelo menos dois, em bloco de código, de verdade usados. Prompt genérico
   ("gere um PRD") não conta como prompt customizado — mostre o que tornou o resultado específico.
5. **Iterações e ajustes** — os momentos em que a saída veio errada ou rasa e o que foi feito. Esta é a
   seção mais valiosa e a mais fácil de falsificar: cite o erro concreto, não "a IA às vezes alucinava".
6. **Como navegar a entrega** — caminho dos arquivos e ordem sugerida de leitura.

## Honestidade

Registrar as correções reais, inclusive as constrangedoras: caminho de arquivo inventado, requisito que
tinha sido descartado na reunião, número parafraseado, documento que repetia outro. É o que dá
credibilidade ao restante e é o que ensina quem for repetir o processo.

Se uma métrica ou abordagem foi testada e abandonada, dizer qual e por quê.

## Erros comuns

- Descrever o processo idealizado em vez do que aconteceu.
- Prompts "de exemplo" que nunca foram executados.
- Contar iterações sem dizer o que mudou em cada uma.
- Transformar a seção de ferramentas em propaganda.
