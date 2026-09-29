#!/usr/bin/env bash
# Cria/recria os symlinks entre mind/claude-user/ e ~/.claude/, pra que as
# Skills/Subagentes/CLAUDE.md de nível usuário sejam lidos pelo Claude Code
# a partir do conteúdo versionado neste repo. Rodar uma vez por máquina,
# depois de um `git clone` (ver docs/ARQUITETURA.md, seção 6).
set -euo pipefail

MIND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_USER_DIR="$MIND_DIR/claude-user"
TARGET_DIR="$HOME/.claude"

link() {
  local src="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if [ -L "$dest" ]; then
    rm "$dest"
  elif [ -e "$dest" ]; then
    echo "AVISO: $dest já existe e não é um symlink — pulando. Mova/apague manualmente e rode de novo se quiser linkar." >&2
    return
  fi
  ln -s "$src" "$dest"
  echo "linkado: $dest -> $src"
}

link "$CLAUDE_USER_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md"

# Aponta pra raiz do vault, pra o CLAUDE.md de usuário achar persona.md e config.md
# de qualquer projeto, sem caminho fixo (ver docs/ARQUITETURA.md, "Persona espelho").
link "$MIND_DIR" "$TARGET_DIR/mind-vault"

if [ -d "$CLAUDE_USER_DIR/skills" ]; then
  for skill_dir in "$CLAUDE_USER_DIR"/skills/*/; do
    [ -d "$skill_dir" ] || continue
    name="$(basename "$skill_dir")"
    link "${skill_dir%/}" "$TARGET_DIR/skills/$name"
  done
fi

if [ -d "$CLAUDE_USER_DIR/agents" ]; then
  for agent_file in "$CLAUDE_USER_DIR"/agents/*.md; do
    [ -f "$agent_file" ] || continue
    name="$(basename "$agent_file")"
    link "$agent_file" "$TARGET_DIR/agents/$name"
  done
fi

echo "Concluído."
