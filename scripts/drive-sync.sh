#!/usr/bin/env bash
# Espelha os binários do vault (ou de um repo de projeto) no Drive, via rclone.
# O GitHub só leva texto; binário fica no disco e tem cópia no Drive, na mesma árvore de pastas.
# O que conta como binário vem do .gitignore da pasta (fonte única): as linhas "*.ext" e as
# linhas com caminho que terminam em "/" ou "*.ext" (ex.: "marca/*/png/", "contratos/*.pdf").
# Sempre "rclone copy" (nunca "sync"): nada é apagado de nenhum dos lados.
#
# Uso: scripts/drive-sync.sh push|pull [pasta-local] [remote:caminho] [--dry-run]
#   push  disco -> Drive (rodar depois de guardar arquivo novo)
#   pull  Drive -> disco (máquina nova: clonar, configurar o rclone, rodar o pull)
#   padrão: a raiz deste vault e $MIND_DRIVE_REMOTE (ou gdrive:mind)
set -euo pipefail
MODE="${1:-}"; shift || true
DRY=()
ARGS=()
for a in "$@"; do [ "$a" = "--dry-run" ] && DRY=(--dry-run) || ARGS+=("$a"); done
LOCAL="${ARGS[0]:-$(cd "$(dirname "$0")/.." && pwd)}"
REMOTE="${ARGS[1]:-${MIND_DRIVE_REMOTE:-gdrive:mind}}"

case "$MODE" in push|pull) ;; *) sed -n '2,11p' "$0"; exit 2 ;; esac
command -v rclone >/dev/null || { echo "rclone não instalado (ver claude-user/CLAUDE.md, regra de binários)"; exit 1; }
rclone listremotes | grep -qx "${REMOTE%%:*}:" || { echo "remote '${REMOTE%%:*}' não configurado: rode 'rclone config'"; exit 1; }

# Padrões binários do .gitignore da pasta; sem .gitignore, usa a do vault.
GI="$LOCAL/.gitignore"; [ -f "$GI" ] || GI="$(cd "$(dirname "$0")/.." && pwd)/.gitignore"
# Regras do rclone em ordem: primeiro as pastas fora, depois cada extensão dentro, por fim todo o resto fora.
FILTER=()
for d in .git node_modules .obsidian .trash .claude; do FILTER+=(--filter "- $d/**"); done
n=0
while read -r ext; do FILTER+=(--filter "+ *.$ext" --filter "+ *.${ext^^}"); n=$((n+1)); done \
  < <(grep -oE '^\*\.[A-Za-z0-9]+$' "$GI" | cut -c3- | sort -u)
# Caminhos (pasta "x/*/png/" ou arquivo "x/*.pdf"), ancorados na raiz como no .gitignore; node_modules e build ficam fora.
while read -r pat; do
  pat="/${pat#/}"; [[ "$pat" == */ ]] && pat="$pat**"
  FILTER+=(--filter "+ $pat"); n=$((n+1))
done < <(grep -E '^[^#!].*/' "$GI" | grep -E '(/|\*\.[A-Za-z0-9]+)$' | grep -vE '(^|/)(node_modules|build)/' | sort -u)
[ "$n" -gt 0 ] || { echo "nenhum padrão binário ('*.ext' ou caminho) em $GI"; exit 1; }
FILTER+=(--filter "- *")

if [ "$MODE" = push ]; then SRC="$LOCAL"; DST="$REMOTE"; else SRC="$REMOTE"; DST="$LOCAL"; fi
echo "$MODE: $SRC -> $DST"
rclone copy "$SRC" "$DST" "${FILTER[@]}" "${DRY[@]}" --stats-one-line --stats 10s -P
