---
tags: [engine, scripts]
criado: 2026-10-20
atualizado: 2026-11-24
---

# Scripts do Mind

Utilitários locais, rodados sob demanda (nenhum é daemon), em Python 3 sem dependência externa, iguais em Windows, Linux e macOS. Um ponto de entrada só: `python scripts/mind.py <comando>` (no Linux sem o alias `python`, instalar `python-is-python3`). Decisões e motivo da troca do bash por Python em [migração pro Windows](../docs/migracao-windows.md). Voltar ao [índice](../MIND.md).

- [mind.py](mind.py) — ponto de entrada; `python scripts/mind.py --help` lista os comandos.
- [mind_cli/main.py](mind_cli/main.py) — despacha o comando pedido pro módulo certo; [mind_cli/__init__.py](mind_cli/__init__.py) marca o pacote.
- [mind_cli/common.py](mind_cli/common.py) — raiz do vault, regra de pastas ignoradas, saída em UTF-8 e busca sem acento, usados por todos os comandos.
- [mind_cli/platform_.py](mind_cli/platform_.py) — tudo que muda de sistema pra sistema (symlink, navegador, subprocesso); o único lugar com `if Windows`.
- `status` ([status.py](mind_cli/status.py)) — varre os repos git irmãos e mostra quais têm mudança não commitada ou commit não enviado.
- `buscar` ([buscar.py](mind_cli/buscar.py)) — busca um termo no vault inteiro (conteúdo e nome, sem acento nem maiúscula) e devolve só os arquivos que mais citam, com uma linha de contexto; usar antes de dizer que o Mind não tem uma informação.
- `orfaos` ([orfaos.py](mind_cli/orfaos.py)) — lista os arquivos que nenhum `.md` linka (nós soltos no grafo do MindView); roda na [manutenção](../docs/ARQUITETURA.md#11-manutenção-periódica-do-vault).
- `tarefas` ([tarefas.py](mind_cli/tarefas.py)) — lê o board `tarefas/`: `foco` (o que atacar agora), `lista` (filtros por prioridade, área e tipo) e `check` (ID duplicado, dependência quebrada, sem marcador, linha longa, prazo vencido, ideia velha); só leitura, e o `check` roda dentro do `vault`.
- `ferramentas` ([ferramentas.py](mind_cli/ferramentas.py)) — mostra quais ferramentas do [registro](../docs/ferramentas.md) estão instaladas nesta máquina (Python, Git, Node, rclone, ffmpeg, MCP do DevTools) e a dica de instalação do seu sistema; `devtools` mostra (ou `--aplicar` roda) o registro do `chrome-devtools` no `claude`.
- `output` ([output.py](mind_cli/output.py)) — pasta de saída das entregas do Claude (fora do vault): mostra e cria o caminho (`config.md` ou `output-mind` em Documentos), `--fixar` fixa no acesso rápido e `lista --antigos N` lista o que passou de N dias, sem apagar nada.
- `drive` ([drive.py](mind_cli/drive.py)) — espelha os binários no Drive via rclone (`push` disco→Drive, `pull` Drive→disco numa máquina nova); extensões tiradas do `.gitignore`, sempre `rclone copy`, nunca apaga nada.
- `vault` ([vault.py](mind_cli/vault.py)) — varredura completa da manutenção semanal: projetos dentro do vault, binários versionados/pesados, duplicados, boards, READMEs-diário, nós grandes e órfãos (só lê e reporta).
- `tamanho` ([tamanho.py](mind_cli/tamanho.py)) — lista os nós `.md` acima do limite de linhas da regra de split (padrão 150); a manutenção só propõe o split.
- `template` ([template.py](mind_cli/template.py)) — avisa se o engine deste vault está atrás do `mind-template` (só leitura).
- `setup` ([setup.py](mind_cli/setup.py)) — recria os symlinks de `claude-user/` em `~/.claude/` depois de um `git clone`; no Windows exige o Modo Desenvolvedor.
- `mensagens` ([mensagens.py](mind_cli/mensagens.py)) — extrai dos transcripts locais só as mensagens do usuário, matéria-prima da mineração da [persona](../persona.md).
- `hook` ([hooks.py](mind_cli/hooks.py)) — avisos do início de sessão do Claude Code (config pendente, manutenção vencida, link do vault ausente); chamado pelo `.claude/settings.json`.
