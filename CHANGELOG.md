# Changelog do engine do Mind

Versão da **base de engenharia** — Skill, `claude-user/`, `docs/ARQUITETURA.md`, `scripts/`, hooks do `.claude/settings.json`. O número em [`VERSION`](VERSION) sobe quando essa base muda de um jeito que um vault já existente vale a pena puxar. Conteúdo pessoal (seus nós, `MIND.md` preenchido, `tarefas/`) nunca afeta esse número.

A rodada de **manutenção periódica** (ver `docs/ARQUITETURA.md`, seção 11) compara o `VERSION` local com o do `mind-template` e avisa quando você está atrás — ela nunca aplica update sozinha, só aponta e te ajuda a aplicar (`git merge upstream/main` se você usa o fluxo de dois remotes, ou à mão).

## v1 — 2026-08-31

Primeira versão numerada. Base de engenharia consolidada, incluindo:

- **`tarefas/` cresce por split.** Cada lista (`pessoal`, `empresa` por padrão) começa como um arquivo único e, ao passar de ~120-150 linhas, vira uma pasta com índice + sub-nós — mesma regra de split de qualquer nó.
- **Rodada periódica renomeada de "otimização" pra "manutenção".** Ela faz mais que otimizar: dedup de histórico + compactação de detalhe operacional + reconciliação com vault complementar + propagação de convenções novas + checagem de versão do template.
- **Checagem de versão do template** na rodada de manutenção, via [`scripts/check-template-version.sh`](scripts/check-template-version.sh) — usa o `../mind-template` local se existir, senão o remote `upstream`, senão pula.
- **Reconciliação com vault complementar** passa a cobrir também decisões registradas no board de `tarefas/` que ainda não chegaram aos nós de produto/conhecimento.
