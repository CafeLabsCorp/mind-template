#!/usr/bin/env bash
# check-template-version.sh — reports whether this vault's ENGINE (Skill, CLAUDE.md,
# ARQUITETURA, scripts, hooks) is behind the mind-template. Read-only: never merges,
# never edits, never commits. Run by the periodic maintenance round; safe anytime.
#
# It finds the template version without needing a local clone of the template:
#   1. a sibling ../mind-template/VERSION, if you happen to keep one checked out
#   2. the 'upstream' git remote (the two-remote fork flow from the README):
#      git fetch upstream --quiet, then read VERSION from upstream/main
#   3. otherwise: skip, with a hint on how to enable the check
set -u

here="$(cd "$(dirname "$0")/.." && pwd)"
digits() { tr -dc '0-9'; }

local_ver="$(cat "$here/VERSION" 2>/dev/null | digits)"
[ -z "$local_ver" ] && local_ver=0

remote_ver=""
source_desc=""

sibling="$(dirname "$here")/mind-template/VERSION"
if [ -f "$sibling" ]; then
  remote_ver="$(cat "$sibling" 2>/dev/null | digits)"
  [ -n "$remote_ver" ] && source_desc="../mind-template (clone local)"
fi

if [ -z "$remote_ver" ] && git -C "$here" remote get-url upstream >/dev/null 2>&1; then
  if git -C "$here" fetch upstream --quiet 2>/dev/null; then
    remote_ver="$(git -C "$here" show upstream/main:VERSION 2>/dev/null | digits)"
    [ -n "$remote_ver" ] && source_desc="remote 'upstream' ($(git -C "$here" remote get-url upstream 2>/dev/null))"
  fi
fi

if [ -z "$remote_ver" ]; then
  echo "TEMPLATE_CHECK: skipped — template não encontrado (nem ../mind-template, nem remote 'upstream')."
  echo "  Para habilitar: git remote add upstream https://github.com/CafeLabsCorp/mind-template.git"
  exit 0
fi

if [ "$local_ver" -ge "$remote_ver" ]; then
  echo "TEMPLATE_CHECK: em dia — engine local v$local_ver, template v$remote_ver (via $source_desc)."
else
  echo "TEMPLATE_CHECK: ATRÁS — engine local v$local_ver, template v$remote_ver (via $source_desc)."
  echo "  Veja o CHANGELOG.md do template para o que mudou entre v$local_ver e v$remote_ver."
  echo "  Aplicar: 'git fetch upstream && git merge upstream/main' (fluxo de dois remotes), ou à mão."
fi
