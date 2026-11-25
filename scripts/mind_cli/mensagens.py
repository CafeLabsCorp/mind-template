"""Extrai, dos transcripts locais do Claude Code (~/.claude/projects/**/*.jsonl), só as mensagens
ESCRITAS PELO USUÁRIO — matéria-prima da mineração da persona espelho (docs/ARQUITETURA.md).
Tudo local: só lê arquivos e imprime na saída padrão; não altera nada.

Descarta: respostas do Claude, resultados de ferramentas, prompts de subagente, mensagens meta/de
sistema (<command-name>, <system-reminder>…), interrupções, mensagens longas demais (provavelmente
conteúdo colado) e duplicatas exatas.

Uso: mind.py mensagens [--since AAAA-MM-DD] [--limit N] [--max-chars N] [--dir DIR]
  --since      só mensagens de DATA em diante (padrão: tudo)
  --limit      no máximo N mensagens, as mais recentes (padrão: 300)
  --max-chars  descarta mensagens maiores que isso (padrão: 600)
  --dir        pasta dos transcripts (padrão: ~/.claude/projects)
"""
import json
import re
import sys
from pathlib import Path

from .platform_ import claude_home

NOISE = re.compile(r"<(system-reminder|ide_[a-z_]+|pasted_content)[^>]*>.*?</\1>", re.S)


def main(args) -> int:
    since, limit, maxchars, d = "", 300, 600, claude_home() / "projects"
    it = iter(args)
    for a in it:
        if a == "--since":
            since = next(it)
        elif a == "--limit":
            limit = int(next(it))
        elif a == "--max-chars":
            maxchars = int(next(it))
        elif a == "--dir":
            d = Path(next(it))
        else:
            print(f"argumento desconhecido: {a}", file=sys.stderr)
            return 2
    if not d.is_dir():
        print(f"pasta de transcripts não encontrada: {d}", file=sys.stderr)
        return 1

    out, seen = [], set()
    for p in sorted(d.rglob("*.jsonl")):
        try:
            fh = open(p, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("type") != "user" or rec.get("isSidechain") or rec.get("isMeta"):
                    continue
                ts = rec.get("timestamp") or ""
                if since and ts[:10] < since:
                    continue
                c = (rec.get("message") or {}).get("content")
                if isinstance(c, list):
                    c = "\n".join(b.get("text", "") for b in c
                                  if isinstance(b, dict) and b.get("type") == "text")
                if not isinstance(c, str):
                    continue
                c = NOISE.sub("", c).strip()
                if not c or c.startswith("<") or c.startswith("[Request interrupted"):
                    continue
                if len(c) > maxchars or c in seen:
                    continue
                seen.add(c)
                out.append((ts, " ".join(c.split())))
    out.sort()
    for ts, text in out[-limit:]:
        print(f"- [{ts[:10]}] {text}")
    return 0
