[Read in English](README.md)

# Mind — template

Base de conhecimento pessoal organizada como uma árvore de Markdown, feita pra ser editada visualmente num editor tipo [Obsidian](https://obsidian.md) e consultada sob demanda pelo **[Claude Code](https://claude.com/claude-code)** — o CLI oficial da Anthropic. Este repositório só funciona de verdade com ele: é o `claude` rodando no seu terminal que lê a Skill e o gatilho daqui e decide quando consultar/salvar algo. Sem o Claude Code instalado, o vault é só uma pasta de Markdown comum.

Este repositório é a **versão crua/template**: só a engenharia (Skill, gatilho de captura, script de symlink, docs de arquitetura), sem nenhum conteúdo pessoal. Clone, personalize e comece a preencher com seus próprios nós.

A arquitetura completa (por que cada decisão foi tomada, o que ainda falta) está em [docs/ARQUITETURA.md](docs/ARQUITETURA.md). Este README é só o "como usar".

## Pré-requisitos

- **[Claude Code](https://claude.com/claude-code) instalado** e configurado (`claude` disponível no terminal) — ver o guia oficial de instalação no link.
- Opcional: um editor de Markdown com suporte a grafo/backlinks, tipo [Obsidian](https://obsidian.md), pra navegar e editar os nós visualmente. Não é obrigatório — dá pra usar só com o terminal.

## O que tem aqui

- **`MIND.md`**: índice raiz, começa vazio. Não existe uma árvore de pastas fixa pré-criada — os nós (e as pastas que fizerem sentido pra organizá-los) vão nascendo aos poucos, conforme as conversas.
- **`.claude/`**: Skill e permissões que só valem quando este projeto está ativo.
- **`claude-user/`**: o "armazém" da Skill, Subagentes e instrução de **nível usuário** — funcionam em qualquer projeto ativo, não só neste. Ficam aqui (versionados neste repo) e são espelhados em `~/.claude/` via symlink (ver abaixo).
- **`scripts/setup-symlinks.sh`**: recria os symlinks de `claude-user/` em `~/.claude/`.
- **`scripts/status-all.sh`**: varre os repos de projeto que você listar dentro dele e mostra quais têm mudança não commitada ou commit não empurrado — pra checar tudo de uma vez em vez de entrar pasta por pasta.
- **`scripts/check-template-version.sh`**: informa se a sua base de engenharia está atrás deste template (só leitura).
- **`VERSION` / `CHANGELOG.md`**: número de versão da base de engenharia e o que mudou em cada bump — usados pela checagem acima e pela rodada de manutenção.

## Setup numa máquina nova

Clone como um fork "manual" via git (dois remotes) — assim dá pra puxar atualizações futuras
do template (seção abaixo) sem perder seus próprios nós. **Não** use o botão "Use this
template" do GitHub: ele gera um histórico git desconectado do original e quebra esse fluxo
(motivo completo em [docs/ARQUITETURA.md](docs/ARQUITETURA.md), seção 12).

1. Crie um repositório **vazio e privado** (GitHub, GitLab, etc.) pra guardar o seu vault —
   não inicialize com README/license/gitignore, tem que ficar realmente vazio.
2. Clone o template e reaponte pra esse repo vazio — use SSH se já tiver uma chave configurada
   no GitHub (não pede senha depois), ou HTTPS se não tiver (funciona sempre, mas pede
   usuário/token a cada push). Pode misturar: `upstream` num protocolo e `origin` no outro, sem
   problema.

   **Via SSH:**

   ```bash
   git clone git@github.com:CafeLabsCorp/mind-template.git mind
   cd mind
   git remote rename origin upstream
   git remote add origin <url-ssh-do-seu-repo-vazio>
   git push -u origin main
   ```

   **Via HTTPS:**

   ```bash
   git clone https://github.com/CafeLabsCorp/mind-template.git mind
   cd mind
   git remote rename origin upstream
   git remote add origin <url-https-do-seu-repo-vazio>
   git push -u origin main
   ```

3. Rode o setup e comece a usar:

   ```bash
   ./scripts/setup-symlinks.sh
   claude
   ```

Pode clonar com o nome que quiser e em qualquer caminho — não há exigência de local fixo, a menos que você use uma integração por voz (ver seção abaixo).

Rodar `./scripts/setup-symlinks.sh` de novo é seguro a qualquer momento (idempotente) — necessário só quando uma Skill/Subagente novo for adicionado em `claude-user/`.

A partir daí é só conversar: peça pra consultar algo, ou comente algo que valha a pena guardar — a Skill e o gatilho cuidam do resto (ver seção abaixo).

## Recebendo atualizações do template

Este repositório evolui (novas regras na Skill, ajustes na arquitetura). Como o setup acima já deixou o `upstream` configurado, puxar atualizações depois é sempre:

```bash
git fetch upstream
git merge upstream/main
```

Isso costuma fundir sem conflito porque a arquitetura já separa o que é "engenharia" (`docs/`, `claude-user/`, `scripts/`, `.claude/`) — que só muda aqui, no template — do que é conteúdo pessoal (`MIND.md` preenchido e as pastas de nós que você for criando) — que o template nunca toca. O ponto de atrito esperado é `.claude/settings.json`: ele acumula permissões liberadas conforme o uso, então se você e o template mudarem esse arquivo ao mesmo tempo pode dar conflito de merge ali — raro, e resolve na mão sem mistério (arquivo pequeno). Mais detalhes da decisão em [docs/ARQUITETURA.md](docs/ARQUITETURA.md), seção 12.

**Saber quando você está atrás:** a base de engenharia tem um número de versão em [`VERSION`](VERSION), e cada bump é descrito em [`CHANGELOG.md`](CHANGELOG.md). A rodada de manutenção periódica (seção abaixo) roda `scripts/check-template-version.sh`, que compara o seu `VERSION` local com o do template e avisa se você está atrás — só reporta, o `git merge` acima continua sendo decisão sua. A checagem não precisa de cópia local do template: usa um `../mind-template` irmão se você mantiver um, senão `git fetch upstream`.

## Como a captura de conhecimento funciona

Durante qualquer conversa com o Claude Code, em qualquer projeto, se algo parecer um fato/decisão/preferência pessoal que valha a pena guardar, o Claude pergunta antes de salvar. Se confirmado, ele mesmo edita o nó certo (ou cria um novo) e atualiza o índice em `MIND.md`. A lógica completa está em `claude-user/CLAUDE.md` (gatilho) e `claude-user/skills/mind/SKILL.md` (procedimento).

Nada é salvo sem confirmação — e nada impede edição manual direta a qualquer momento; o Claude só lê o estado atual dos arquivos quando consultado.

## Integração por voz (opcional)

É possível plugar um assistente de voz externo que resolve "projeto ativo" por voz e roda o Claude Code apontado pra ele. É totalmente opcional — sem isso, o Mind funciona normalmente só com Claude Code no teclado. Detalhes do padrão geral estão em `docs/ARQUITETURA.md`, seção 8.

## Time de agentes de desenvolvimento (opcional)

O Mind organiza conhecimento pessoal — não inclui um time de agentes pra desenvolver software. Se você também constrói produtos/MVPs e quer um padrão de orquestrador + especialistas pra acelerar isso, [Café Labs Forge](https://github.com/CafeLabsCorp/forge) é um complemento pronto e totalmente desacoplado (repositório próprio, não depende do Mind nem vice-versa). Detalhes em `docs/ARQUITETURA.md`, seção 9.

## Repositório privado depois de preenchido

Assim que você começar a adicionar nós de conhecimento com informação pessoal, mantenha o repositório privado. Toda a "engenharia" deste template (Skill, script de symlink, estrutura, este README, `docs/ARQUITETURA.md`) é genérica e pode continuar pública/compartilhável — o que precisa ficar privado é só o conteúdo que você for criando.
