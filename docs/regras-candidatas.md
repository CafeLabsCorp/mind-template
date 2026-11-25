---
tags: [manutencao, regras]
criado: 2026-11-25
---

# Regras candidatas

Fila de **possíveis regras de trabalho** anotadas durante as conversas, pra decidir na rodada de manutenção (ver [ARQUITETURA.md](ARQUITETURA.md), seção 13). Quando uma correção sua, uma preferência ou uma abordagem que deu certo parece valer como regra, o Claude anota uma linha aqui **sem pedir permissão** e avisa em uma frase. Nada daqui vale como regra até ser promovido: a promoção só acontece na rodada, com o seu sim. Não é nó de conhecimento (não segue a regra de tamanho/split).

## Como anotar

Uma linha por candidata, sem narrar a conversa:

`- (data) **regra** — motivo. _Origem:_ projeto/peça. _Sugestão:_ regra de trabalho | projeto:<nome> | persona | conhecimento | descartar. ^rc-<id>`

- Antes de anotar, ver se já existe uma parecida: se sim, só acrescentar a nova origem e a data na linha existente (repetição é sinal de que a regra vale).
- Regra que você pediu explicitamente pra registrar ("anota como regra") não passa por aqui: vai direto pro `claude-user/CLAUDE.md`.
- Lição técnica sem comportamento ("tal comando falha em tal caso") vai como sugestão `conhecimento`.

## Como decidir na rodada

Pra cada candidata em aberto, o Claude propõe o destino com o motivo, em lote e numerado: **regra de trabalho** (`claude-user/CLAUDE.md`), **projeto** (CLAUDE.md ou nó do projeto, só se você disser que vale só ali), **persona** (traço de comportamento), **conhecimento** (nó em `conhecimentos/`) ou **descartar**. Só aplica depois do "pode". O que foi decidido sai de "Em aberto" e vira uma linha em "Resolvidas" (data, destino); o motivo completo fica na regra promovida.

## Em aberto

_Nenhuma ainda._

## Resolvidas

_Nenhuma ainda._

## Ver também

- [../MIND.md](../MIND.md) — índice do Mind.
- [ARQUITETURA.md](ARQUITETURA.md) — como o Mind funciona e por quê.
