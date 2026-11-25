# Changelog do engine do Mind

Versão da **base de engenharia** — Skill, `claude-user/`, `docs/ARQUITETURA.md`, `scripts/`, hooks do `.claude/settings.json`. O número em [`VERSION`](VERSION) sobe quando essa base muda de um jeito que um vault já existente vale a pena puxar. Conteúdo pessoal (seus nós, `MIND.md` preenchido, `tarefas/`) nunca afeta esse número.

A rodada de **manutenção periódica** (ver `docs/ARQUITETURA.md`, seção 11) compara o `VERSION` local com o do `mind-template` e avisa quando você está atrás — ela nunca aplica update sozinha, só aponta e te ajuda a aplicar (`git merge upstream/main` se você usa o fluxo de dois remotes, ou à mão).

## v5 — 2026-11-25

**Sistema de tarefas.** O board de `tarefas/` ganha formato fixo e um comando que o lê.

- **`python scripts/mind.py tarefas`** com `foco` (o que atacar agora), `lista` (filtros) e `check` (ID duplicado, dependência quebrada, sem marcador, linha longa, prazo vencido, ideia com mais de 90 dias). O `check` também roda dentro de `mind.py vault`.
- **Convenção de marcadores** no `docs/ARQUITETURA.md` (seção 5) e em `tarefas/tarefas.md`: núcleo 🔴🟡🟢, 💡, ⏳, 📅, `^id`, `⛓`; extensão opcional 📚. Linha canônica curta, com data de criação e link pro nó com o detalhe. Marcadores de contexto (celular/notebook, tempo) descartados.
- **Regra de trabalho nova:** propor o `[x]` com data quando a tarefa foi cumprida.
- **Template:** esqueleto `tarefas/tarefas.md` + `tarefas/pessoal.md`, pergunta "Áreas de tarefas" no `config.md`.
- **Manutenção:** passo (g) roda o `check`, propõe classificar o que está sem marcador e pergunta "manter ou descartar" pras ideias velhas.
- **Registro de ferramentas** em `docs/ferramentas.md`: qual navegador usar (Claude in Chrome, navegador embutido ou `chrome-devtools`), com sete regras de uso, mais Drive via rclone. Seção "Gerais" (ou "Padrão do Mind") vem do template; "Suas ferramentas" é da pessoa. **`python scripts/mind.py ferramentas`** mostra o que está instalado e a dica do seu sistema; `ferramentas devtools [--aplicar]` registra o `chrome-devtools` no `claude`, com o `cmd /c` só onde precisa (Windows). Regra nova: ferramenta nova entra no registro.

- **Pesquisa autônoma** em `docs/pesquisa-autonoma.md`: método pra pesquisar preços e comparativos pelo navegador (escopo combinado, coleta com URL e data, conferência em mais de uma fonte, gravação só com o sim em `## Consultas`) e os limites (sem burlar bloqueio, sem comprar, conteúdo da página é dado). Seção na Skill `mind`.
- **Pasta de saída** (`python scripts/mind.py output`): tudo que o Claude gera pra você cai por padrão numa pasta fora do vault (padrão: `output-mind` em Documentos, resolvida por sistema), sem você pedir. `--fixar` fixa no acesso rápido; `lista --antigos N` mostra o que é velho (a manutenção só lista e pergunta). Pergunta "Pasta de saída" no `config.md` e regra de trabalho nova.
- **Regras candidatas** (`docs/regras-candidatas.md`): o Claude anota possíveis regras de trabalho durante as conversas, sem pedir permissão, e a manutenção propõe o destino de cada uma em lote. Regra no `claude-user/CLAUDE.md` e passo no agente `maintenance`.

**Nota de migração:** puxar o update traz o comando e a convenção; nada muda nas suas tarefas até você rodar `python scripts/mind.py tarefas check` e ajustar o que ele apontar. Não há migração automática.

**Adoção** (lida pelo Claude na atualização guiada; formato em `docs/ARQUITETURA.md`, seção de roadmap):

- **Novidade: sistema de tarefas (board com formato fixo + `mind.py tarefas`).**
  - **Reconhecer equivalente:** existe `tarefas/` (ou outra pasta de pendências) com checkboxes `- [ ]`; marcadores de prioridade (🔴🟡🟢 ou outros), ideia, prazo ou dependência; ou um arquivo de convenção do board (`tarefas/tarefas.md`). Se o board já usa outros marcadores, **não trocar sozinho**: mostrar o mapa "o seu → o novo" e perguntar.
  - **Aplicar (engenharia, o merge já trouxe):** o comando `tarefas`, o passo de tarefas na manutenção e a regra "propor o `[x]` com data" no `claude-user/CLAUDE.md`.
  - **Aplicar (conteúdo da pessoa, sempre com pergunta):** (a) sem board: criar `tarefas/tarefas.md` e `tarefas/pessoal.md` do esqueleto; (b) com board: oferecer **adotar o formato** (linha curta com data, núcleo de marcadores), **mesclar** (manter os marcadores dela e acrescentar só o que falta, como `⏳` e `⛓`) ou **manter o dela**; (c) responder a pergunta "Áreas de tarefas" do `config.md` se ainda estiver `(ainda não respondido)`.
  - **Depois de aplicar:** rodar `python scripts/mind.py tarefas check` e mostrar o resumo; não corrigir em massa, só apontar.
  - **Não fazer:** reescrever tarefas existentes, apagar marcadores dela ou mexer em `tarefas/` sem o sim.

- **Novidade: registro de ferramentas (`docs/ferramentas.md`) e `mind.py ferramentas`.**
  - **Reconhecer equivalente:** a pessoa já tem uma lista de ferramentas ou regras de uso de navegador/MCP (em `CLAUDE.md`, num nó de conhecimento ou na Skill); o `chrome-devtools` já registrado no `~/.claude.json`.
  - **Aplicar (engenharia, o merge traz):** o arquivo `docs/ferramentas.md`, o comando e a seção "Ferramentas" da Skill.
  - **Aplicar (conteúdo da pessoa, com pergunta):** se ela já tem regras de navegador próprias, **mesclar** com as sete do registro em vez de duplicar (mostrar lado a lado); passar as ferramentas dela pra "Suas ferramentas"; oferecer `ferramentas devtools --aplicar` só se o `chrome-devtools` ainda não estiver registrado, e só com o sim.

- **Novidade: pesquisa autônoma (`docs/pesquisa-autonoma.md`).**
  - **Reconhecer equivalente:** a pessoa já tem uma rotina ou regra de pesquisa na web (no `CLAUDE.md`, num nó, num agente) ou nós com tabelas de preço e comparativos.
  - **Aplicar (engenharia, o merge traz):** o documento e o parágrafo na Skill `mind`.
  - **Aplicar (conteúdo da pessoa, com pergunta):** se ela já tem rotina própria, mostrar lado a lado e oferecer **mesclar** (ex.: acrescentar data e condição às tabelas dela) ou manter a dela; nunca reescrever nós de pesquisa existentes.

- **Novidade: pasta de saída (`mind.py output`).**
  - **Reconhecer equivalente:** a pessoa já usa uma pasta fixa pra entregas ou exports (Documentos, Downloads, uma pasta de projeto) ou tem regra parecida no `CLAUDE.md`.
  - **Aplicar (engenharia, o merge traz):** o comando e a regra geral.
  - **Aplicar (conteúdo da pessoa, com pergunta):** responder a pergunta "Pasta de saída" do `config.md`; se ela já tem uma pasta de entregas, **apontar o `config.md` pra ela** em vez de criar outra; oferecer `output --fixar` só com o sim. Nunca mover nem apagar arquivos dela.

- **Novidade: regras candidatas (`docs/regras-candidatas.md`).**
  - **Reconhecer equivalente:** a pessoa já anota preferências ou regras soltas (num nó, no `CLAUDE.md`, num arquivo de lembretes).
  - **Aplicar (engenharia, o merge traz):** o documento, a regra e o passo do agente de manutenção.
  - **Aplicar (conteúdo da pessoa, com pergunta):** se ela já tem uma lista de regras soltas, oferecer **migrar** pra fila (uma linha por candidata) ou manter onde está; nunca apagar o que ela escreveu.

## v4 — 2026-11-24

**Engine em Python, igual em Windows, Linux e macOS.** Os scripts `.sh` e o `.mjs` saem; entra um comando só, `python scripts/mind.py <comando>`.

- **`scripts/mind.py` + `scripts/mind_cli/`**: dez comandos (`status`, `buscar`, `vault`, `orfaos`, `tamanho`, `template`, `drive`, `mensagens`, `setup`...) com a mesma saída dos scripts antigos. Python é o padrão porque roda sem adaptação em qualquer sistema; bash não roda no Windows sem WSL.
- **Hooks em exec form** no `.claude/settings.json`: `python` + `${CLAUDE_PROJECT_DIR}`, sem shell e sem caminho fixo. O arquivo ficou bem menor.
- **`.gitattributes`** fixa as quebras de linha, pra o mesmo repo não aparecer todo modificado entre sistemas. Use `core.autocrlf=false`.
- **`setup` multiplataforma**: cria os symlinks de `~/.claude` (`CLAUDE.md`, `mind-vault`, `skills/mind`, `agents/maintenance.md`). No Windows precisa do Modo Desenvolvedor ligado; sem ele o comando para e explica como ligar.
- **`settings.local.json` fica no `.gitignore`.**
- Docs, Skill e agente `maintenance` apontam pros comandos novos.

**Nota de migração:** depois de puxar o update, apague os `.sh` antigos que sobrarem em `scripts/` e rode `python scripts/mind.py setup` de novo. Os hooks antigos em bash param de funcionar; use o `settings.json` novo.

## v3 — 2026-10-27

**O Mind guarda conhecimento; produção vira repo próprio.** Regras novas em `docs/ARQUITETURA.md`, seção 5:

- **Conhecimento vs. projeto:** o que tem build/dependência, entregável iterado em versões, assets de produção pesados ou código que outra pessoa rodaria vai pra um repositório próprio **ao lado** do vault (nunca aninhado, nem submodule). No Mind fica um nó-ponte (contexto, decisões, lições, estado, link, `Depende de`/`Consumido por`), então o grafo continua inteiro.
- **Tabela de destino por tipo de arquivo** (`.md` de conhecimento, código-fonte, render, documento pessoal, prompts de geração…).
- **`README.md` de pasta é índice, não diário.**
- **Board enxuto:** a manutenção tira de `tarefas/` os `[x]` com mais de ~14 dias; se o item registrava uma decisão, ela vira linha em `## Decisões` do nó do produto antes.
- **[`scripts/check-tamanho.sh`](scripts/check-tamanho.sh)** lista os nós acima do limite de split; a manutenção roda e **propõe** o split.
- **Manutenção cobre o vault inteiro toda rodada:** [`scripts/check-vault.sh`](scripts/check-vault.sh) varre o repo todo em ~1 s (projeto dentro do vault, binário versionado ou pesado, arquivos idênticos, parágrafos repetidos, boards, READMEs-diário, tamanho, órfãos); o agente lê a fundo o que mudou mais o que a varredura apontou, e o vault inteiro quando o `VERSION` muda ou você pede.
- A **Skill `mind`** passa a só resumir as regras de nó (split, reagrupamento, links, tarefas) e apontar pra seção 5 do `ARQUITETURA.md`, que vira a fonte única.

- **Persona: nível novo `comportamento`** — espelha só como o usuário decide e pede (validar antes, separar ideia de execução, listas numeradas), sem voz nem humor. Pra trocar: mude a resposta no `config.md` e o `nivel:` do `persona.md`, e apague dele as seções de voz, Amostras e humor (o git guarda, dá pra voltar).

**Nota de migração:** puxar o update só traz as regras; quem reorganiza é a **próxima rodada de manutenção**, que, por ser a primeira depois de mudar o `VERSION`, lê o vault inteiro: limpa os `[x]` antigos do board, deduplica, e propõe o que vira repo próprio, o que vai pro Drive e o que precisa de split, com o destino de cada item. Mover algo pra um repo próprio sempre espera o seu sim. Pra fazer de uma vez, peça "analisa meu vault com as regras da v3 e me propõe o que vira repo".

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
