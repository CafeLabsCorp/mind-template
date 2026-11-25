"""Lista os arquivos do vault que nenhum .md linka (nós soltos no grafo do MindView).

Uso: mind.py orfaos [raiz-do-vault]   (padrão: a raiz deste repo)
Saída: uma linha por órfão; código de saída 1 se houver algum.
"""
import os
import posixpath
import re
import sys
import urllib.parse
from pathlib import Path

from .common import ROOT, read_text, walk_files


def find_orphans(root: Path):
    files = list(walk_files(root))
    mds = [p for p in files if p.endswith(".md")]
    by_name = {}
    for m in mds:
        by_name.setdefault(posixpath.splitext(posixpath.basename(m))[0].lower(), []).append(m)
    linked = set()
    for m in mds:
        t = read_text(root / m)
        for l in re.findall(r"\]\(([^)\s]+)", t):
            l = urllib.parse.unquote(l.split("#")[0])
            if l and "://" not in l and not l.startswith("mailto:"):
                tgt = posixpath.normpath(posixpath.join(posixpath.dirname(m), l))
                if tgt != m:
                    linked.add(tgt)
        for w in re.findall(r"\[\[([^\]|#]+)", t):
            for hit in by_name.get(posixpath.basename(w).lower(), []):
                if hit != m:
                    linked.add(hit)
    return sorted(p for p in files if p not in linked), len(files)


def main(args) -> int:
    root = Path(args[0]).resolve() if args else ROOT
    orph, total = find_orphans(root)
    for p in orph:
        print(p)
    print(f"{len(orph)} órfão(s) de {total} arquivos", file=sys.stderr)
    return 1 if orph else 0
