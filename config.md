---
tags: [config, mind]
criado: 2026-07-23
atualizado: 2026-07-23
---

# Configuração do Mind

Perguntas de configuração inicial de como o Claude deve trabalhar com este vault e com o usuário — respondidas uma vez, na primeira conversa depois de clonar o vault (ou quando o usuário quiser mudar algo aqui depois). Diferente de `claude-user/CLAUDE.md` (regras de trabalho específicas — convenções de commit, formato de resposta) e de `MIND.md` (índice de conhecimento): este arquivo é só a configuração inicial de funcionamento.

**Se alguma resposta abaixo estiver como `(ainda não respondido)`**, pergunte ao usuário essa(s) pergunta(s) logo no início da conversa (pode agrupar via `AskUserQuestion`), e grave a resposta aqui — substituindo o marcador, não apagando a pergunta.

## Idioma de conversa

Em qual idioma o Claude deve responder por padrão? Opções sugeridas: português, inglês, ou outro (texto livre).

**Resposta:** (ainda não respondido)

## Como quer ser chamado

Nome ou apelido que o Claude deve usar ao se referir ao usuário nas respostas.

**Resposta:** (ainda não respondido)

## Fuso horário

Pra interpretar datas relativas ("amanhã", "sexta") e registrar tarefas/memórias com a data certa.

**Resposta:** (ainda não respondido)

## Tom / formalidade das respostas

Ex.: direto e casual vs. mais formal.

**Resposta:** (ainda não respondido)

## Papel / profissão principal

O que a pessoa faz — bootstrap rápido pra calibrar explicações técnicas desde a primeira conversa (complementa memórias tipo "user" que se acumulam aos poucos com o tempo).

**Resposta:** (ainda não respondido)

## Persona espelho

Quer que o Claude aprenda aos poucos como você fala e age, e passe a conversar no mesmo estilo? Ele grava o perfil em `persona.md` sem pedir permissão a cada mudança (só avisa numa linha), e você pode editar o arquivo à mão ou mudar esta resposta quando quiser. **Custo:** praticamente nenhum — o arquivo é curto (~1k tokens por conversa, com cache) e o aprendizado acontece dentro da própria conversa, sem chamadas extras. Níveis:

- **desligado** — não aprende nada.
- **voz** — só o jeito de falar (registro, expressões, estrutura das mensagens).
- **voz+comportamento** — também como você decide, pede, corrige e reage a erro/risco.
- **voz+comportamento+humor** — também o tipo de humor; só espelha piada quando você puxa.

**Resposta:** (ainda não respondido)

## Mineração de conversas antigas (persona espelho)

Quer que a rodada de manutenção também analise suas conversas antigas com o Claude — só as **suas** mensagens, extraídas localmente por `scripts/extract-user-messages.sh` — pra achar traços de estilo e comportamento que a observação ao vivo não pegou? **Custo:** é a única parte da persona que gasta tokens de verdade, ~20–30k por rodada (a primeira um pouco mais; depois só o que é novo). Traços novos entram com aviso de uma linha; **mensagens literais pra "Amostras" sempre pedem a sua confirmação antes** (podem ter nome de terceiro ou dado privado). Só vale se a persona acima não estiver `desligado`. Opções: **não** / **perguntar** (a rodada pergunta antes de minerar) / **automático** (minera em toda rodada).

**Resposta:** (ainda não respondido)

## Ver também

- [MIND.md](MIND.md)
- [claude-user/CLAUDE.md](claude-user/CLAUDE.md) — regras de trabalho (diferente disto aqui, que é configuração inicial)
