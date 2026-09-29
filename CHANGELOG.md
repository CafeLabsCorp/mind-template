# Changelog do engine do Mind

Versão da **base de engenharia** — Skill, `claude-user/`, `docs/ARQUITETURA.md`, `scripts/`, hooks do `.claude/settings.json`. O número em [`VERSION`](VERSION) sobe quando essa base muda de um jeito que um vault já existente vale a pena puxar. Conteúdo pessoal (seus nós, `MIND.md` preenchido, `tarefas/`) nunca afeta esse número.

A rodada de **manutenção periódica** (ver `docs/ARQUITETURA.md`, seção 11) compara o `VERSION` local com o do `mind-template` e avisa quando você está atrás — ela nunca aplica update sozinha, só aponta e te ajuda a aplicar (`git merge upstream/main` se você usa o fluxo de dois remotes, ou à mão).

## v2 — 2026-09-29

**Persona espelho**: opt-in (com níveis) pra o Claude aprender aos poucos como o usuário fala e age, e conversar no mesmo estilo. Racional e mecanismo em `docs/ARQUITETURA.md` (seção "Persona espelho").

- **`config.md`** ganha a pergunta "Persona espelho" (desligado / voz / voz+comportamento / +humor). O hook de config que já existe pergunta sozinho, porque a resposta nasce como `(ainda não respondido)`.
- **`scripts/setup-symlinks.sh`** cria `~/.claude/mind-vault` → raiz do vault. **Depois de puxar o update, rode `./scripts/setup-symlinks.sh` de novo** — um hook `SessionStart` avisa se você esquecer.
- **`claude-user/CLAUDE.md`** importa `@~/.claude/mind-vault/persona.md` (sem caminho fixo, funciona em qualquer projeto e em qualquer local de clone); **`claude-user/skills/mind/SKILL.md`** ganha o procedimento (níveis, esqueleto, promoção `(inicial)`→`(firme)`, fronteira com regra de trabalho).
- **`claude-user/agents/maintenance.md`** e a rodada de manutenção passam a cuidar do `persona.md` (dedup, tamanho, contradições; só reporta traço `(inicial)` velho).
- **Mineração de conversas antigas** (opt-in separado no `config.md`: não / perguntar / automático): a rodada de manutenção pode analisar suas mensagens antigas via [`scripts/extract-user-messages.sh`](scripts/extract-user-messages.sh) (local, só as suas mensagens, ~300 mais recentes) pra achar traços que a observação ao vivo não pegou. Custo ~20-30k tokens por rodada; Amostras literais sempre pedem confirmação.
- O template **não entrega** `persona.md`: ele nasce no primeiro traço real, no seu vault privado.

**Nota de migração — se você já tinha uma "persona espelho" caseira** (seção com caminho fixo tipo `~/mind/persona.md` no `claude-user/CLAUDE.md`): o `git merge upstream/main` vai conflitar nesse arquivo — aceite a seção do upstream. Seu `persona.md` continua valendo, sem mudança de formato; só acrescente `nivel: <nível>` no frontmatter (o que você já usa é, na prática, `voz+comportamento`) e, se quiser, uma seção `## Amostras` com 5-10 mensagens reais suas — melhora bastante o estilo. Depois: rode o setup, responda a nova pergunta do `config.md` e cheque se sobrou a seção antiga duplicada no `CLAUDE.md`. Um Claude pode fazer esses passos por você: peça "migra minha persona caseira pra v2 do template".

## v1 — 2026-08-31

Primeira versão numerada. Base de engenharia consolidada, incluindo:

- **`tarefas/` cresce por split.** Cada lista (`pessoal`, `empresa` por padrão) começa como um arquivo único e, ao passar de ~120-150 linhas, vira uma pasta com índice + sub-nós — mesma regra de split de qualquer nó.
- **Rodada periódica renomeada de "otimização" pra "manutenção".** Ela faz mais que otimizar: dedup de histórico + compactação de detalhe operacional + reconciliação com vault complementar + propagação de convenções novas + checagem de versão do template.
- **Checagem de versão do template** na rodada de manutenção, via [`scripts/check-template-version.sh`](scripts/check-template-version.sh) — usa o `../mind-template` local se existir, senão o remote `upstream`, senão pula.
- **Reconciliação com vault complementar** passa a cobrir também decisões registradas no board de `tarefas/` que ainda não chegaram aos nós de produto/conhecimento.
