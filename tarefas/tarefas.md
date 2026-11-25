---
tags: [tarefas, produtividade]
criado: 2026-11-25
atualizado: 2026-11-25
---

# Tarefas — índice

O board de tarefas do Mind. Cada tarefa é um checkbox Markdown (`- [ ]` / `- [x]`) com marcadores curtos. Fica tudo em texto, sem ferramenta externa: o comando `python scripts/mind.py tarefas` lê e valida (`foco`, `lista`, `check`). Regra geral: tarefa só mora aqui; os nós de projeto descrevem fatos e apontam pra cá.

## Listas

As áreas são as que você respondeu em [config.md](../config.md) (por padrão, só pessoal). Cada área é um arquivo; quando passar de ~120–150 linhas, vira pasta com índice (regra de split do `docs/ARQUITETURA.md`).

- [Pessoal](pessoal.md) — suas tarefas pessoais.

## Linha canônica

`- [ ] 🟡 **Título curto** (AAAA-MM-DD) — uma frase do que falta. [contexto](../caminho/no.md) ^id`

- **Curta:** até ~300 caracteres. Detalhe, decisão e histórico vão pro nó do projeto, e a linha só aponta pra ele. O `check` avisa quando passa disso.
- **Data de criação** `(AAAA-MM-DD)` logo depois do título, em toda tarefa nova: é ela que deixa a ideia envelhecer e ser revisada.
- **Concluir:** troque `[ ]` por `[x]` e acrescente `(feito AAAA-MM-DD)`. O Claude propõe marcar quando perceber que a tarefa foi cumprida; a manutenção tira os `[x]` com mais de ~14 dias.

## Marcadores

O marcador vem logo depois do `- [ ]`:

- 🔴 **alta**, 🟡 **média**, 🟢 **baixa**. Sem marcador: ainda não classificada (o `check` avisa).
- 💡 **ideia**: nunca entra no foco; a manutenção pergunta "manter ou descartar" quando passa de 90 dias.
- ⏳ **aguardando**: `⏳ aguardando o Pedro responder` no fim da linha (antes do `^id`). Sai do foco e aparece num bloco "aguardando"; tirar a marca devolve a tarefa ao foco.
- 📅 `AAAA-MM-DD`: prazo de verdade. Entra no `foco` quando faltam 7 dias ou menos, e o `check` avisa se vencer.
- **ID** ` ^area-nome` no fim da linha, só quando outra tarefa depende dela ou há prazo.
- ⛓ **dependência**: `⛓ depende de ^id` no fim da linha. A tarefa referenciada precisa ter o ID; o `check` acusa se ele não existir.
- 📚 **estudo** (opcional): fora do foco, mesmo com 🔴. Pode ser ligado ou ignorado.

Pode somar marcas próprias aqui; o `check` ignora as que não conhece.

## Comandos

- `python scripts/mind.py tarefas foco` — o que atacar agora: prazo próximo ou atrasado, 🔴 prontas, 🔴 bloqueadas por dependência, aguardando.
- `python scripts/mind.py tarefas lista [--prio vermelho|amarelo|verde] [--area X] [--tipo ideia|estudo|aguardando] [--todas]`.
- `python scripts/mind.py tarefas check [--tudo]` — erros (ID duplicado, dependência quebrada) e avisos (sem marcador, linha longa, prazo vencido, ideia velha).

## Ver também

- [../MIND.md](../MIND.md) — índice do Mind.
- [../docs/ARQUITETURA.md](../docs/ARQUITETURA.md) — por que o board é assim (seção 5).
