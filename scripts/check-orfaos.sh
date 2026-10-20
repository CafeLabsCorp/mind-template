#!/usr/bin/env bash
# Lista os arquivos do vault que nenhum .md linka (nós soltos no grafo do MindView).
# Mesma regra do MindView: ignora pastas ocultas e .git/node_modules/.obsidian/.trash/venv/__pycache__.
# Uso: scripts/check-orfaos.sh [raiz-do-vault]   (padrão: a raiz deste repo)
# Saída: uma linha por órfão; código de saída 1 se houver algum.
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
exec python3 -I - "$ROOT" <<'PY'
import os, re, sys, urllib.parse
root = sys.argv[1]
SKIP = {'.git', 'node_modules', '.obsidian', '.trash', 'venv', '__pycache__'}
mds, others = [], []
for d, ds, fs in os.walk(root):
    ds[:] = [x for x in ds if x not in SKIP and not x.startswith('.')]
    for f in fs:
        if f.startswith('.'):
            continue
        p = os.path.relpath(os.path.join(d, f), root)
        (mds if f.endswith('.md') else others).append(p)
by_name = {}
for m in mds:
    by_name.setdefault(os.path.splitext(os.path.basename(m))[0].lower(), []).append(m)
linked = set()
for m in mds:
    t = open(os.path.join(root, m), encoding='utf8', errors='ignore').read()
    for l in re.findall(r'\]\(([^)\s]+)', t):
        l = urllib.parse.unquote(l.split('#')[0])
        if l and '://' not in l and not l.startswith('mailto:'):
            tgt = os.path.normpath(os.path.join(os.path.dirname(m), l))
            if tgt != m:
                linked.add(tgt)
    for w in re.findall(r'\[\[([^\]|#]+)', t):
        for hit in by_name.get(os.path.basename(w).lower(), []):
            if hit != m:
                linked.add(hit)
orph = sorted(p for p in mds + others if p not in linked)
for p in orph:
    print(p)
print(f'{len(orph)} órfão(s) de {len(mds) + len(others)} arquivos', file=sys.stderr)
sys.exit(1 if orph else 0)
PY
