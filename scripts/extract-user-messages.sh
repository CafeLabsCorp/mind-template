#!/usr/bin/env bash
# Extrai, dos transcripts locais do Claude Code (~/.claude/projects/**/*.jsonl),
# só as mensagens ESCRITAS PELO USUÁRIO — matéria-prima da mineração da persona
# espelho (docs/ARQUITETURA.md, "Persona espelho"). Tudo local: só lê arquivos
# e imprime na saída padrão; não altera nada.
#
# Descarta: respostas do Claude, resultados de ferramentas, prompts de subagente,
# mensagens meta/de sistema (<command-name>, <system-reminder>…), interrupções,
# mensagens longas demais (provavelmente conteúdo colado) e duplicatas exatas.
#
# Uso: scripts/extract-user-messages.sh [--since AAAA-MM-DD] [--limit N] [--max-chars N] [--dir DIR]
#   --since      só mensagens de DATA em diante (padrão: tudo)
#   --limit      no máximo N mensagens, as mais recentes (padrão: 300)
#   --max-chars  descarta mensagens maiores que isso (padrão: 600)
#   --dir        pasta dos transcripts (padrão: ~/.claude/projects)
set -euo pipefail

SINCE="" LIMIT=300 MAXCHARS=600 DIR="$HOME/.claude/projects"
while [ $# -gt 0 ]; do
  case "$1" in
    --since) SINCE="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --max-chars) MAXCHARS="$2"; shift 2 ;;
    --dir) DIR="$2"; shift 2 ;;
    *) echo "argumento desconhecido: $1" >&2; exit 2 ;;
  esac
done

[ -d "$DIR" ] || { echo "pasta de transcripts não encontrada: $DIR" >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 é necessário" >&2; exit 1; }

find "$DIR" -name '*.jsonl' -print0 | python3 -c '
import sys, json, re

since, limit, maxchars = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
paths = [p for p in sys.stdin.buffer.read().split(b"\0") if p]
noise = re.compile(r"<(system-reminder|ide_[a-z_]+|pasted_content)[^>]*>.*?</\1>", re.S)
out, seen = [], set()

for p in paths:
    try:
        f = open(p, encoding="utf-8", errors="replace")
    except OSError:
        continue
    with f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "user" or d.get("isSidechain") or d.get("isMeta"):
                continue
            ts = d.get("timestamp") or ""
            if since and ts[:10] < since:
                continue
            c = (d.get("message") or {}).get("content")
            if isinstance(c, list):
                c = "\n".join(b.get("text", "") for b in c
                              if isinstance(b, dict) and b.get("type") == "text")
            if not isinstance(c, str):
                continue
            c = noise.sub("", c).strip()
            if not c or c.startswith("<") or c.startswith("[Request interrupted"):
                continue
            if len(c) > maxchars or c in seen:
                continue
            seen.add(c)
            out.append((ts, " ".join(c.split())))

out.sort()
for ts, text in out[-limit:]:
    print("- [%s] %s" % (ts[:10], text))
' "$SINCE" "$LIMIT" "$MAXCHARS"
