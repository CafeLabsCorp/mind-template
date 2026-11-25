"""Lista os nós .md do vault acima do limite de linhas da regra de split (docs/ARQUITETURA.md, seção 5).

Ignora pastas ocultas, node_modules e os logs do engine que crescem por natureza.
Uso: mind.py tamanho [limite] [raiz-do-vault]   (padrão: 150 linhas, a raiz deste repo)
Saída: "linhas  caminho", do maior pro menor; código de saída 1 se houver algum.
"""
import sys
from pathlib import Path

from .common import ROOT, walk_files

EXEMPTOS = {"docs/ARQUITETURA.md", "docs/MANUTENCAO.md", "CHANGELOG.md"}


def find_big(limite: int, root: Path):
    out = []
    for rel in walk_files(root):
        if not rel.endswith(".md") or rel in EXEMPTOS:
            continue
        with open(root / rel, "rb") as fh:
            n = fh.read().count(b"\n")
        if n > limite:
            out.append((n, rel))
    return sorted(out, key=lambda x: (-x[0], x[1]))


def main(args) -> int:
    limite = int(args[0]) if args else 150
    root = Path(args[1]).resolve() if len(args) > 1 else ROOT
    out = find_big(limite, root)
    for n, rel in out:
        print(f"{n:5d}  {rel}")
    print(f"{len(out)} nó(s) acima de {limite} linhas", file=sys.stderr)
    return 1 if out else 0
