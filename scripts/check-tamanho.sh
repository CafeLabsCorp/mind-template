#!/usr/bin/env bash
# Lista os nós .md do vault acima do limite de linhas da regra de split (docs/ARQUITETURA.md, seção 5).
# Ignora pastas ocultas, .git/node_modules/.obsidian e os logs do engine que crescem por natureza.
# Uso: scripts/check-tamanho.sh [limite] [raiz-do-vault]   (padrão: 150 linhas, a raiz deste repo)
# Saída: "linhas  caminho", do maior pro menor; código de saída 1 se houver algum.
set -euo pipefail
LIMITE="${1:-150}"
ROOT="${2:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$ROOT"
out=$(find . -mindepth 1 \( -name '.*' -o -name node_modules \) -prune -o -type f -name '*.md' -print \
  | grep -v -E '^\./(docs/(ARQUITETURA|MANUTENCAO)|CHANGELOG)\.md$' \
  | while read -r f; do n=$(wc -l < "$f"); [ "$n" -gt "$LIMITE" ] && printf '%5d  %s\n' "$n" "${f#./}"; done \
  | sort -rn || true)
[ -n "$out" ] && echo "$out"
echo "$(printf '%s' "$out" | grep -c . || true) nó(s) acima de $LIMITE linhas" >&2
[ -z "$out" ]
