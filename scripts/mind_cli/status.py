"""Varre os repositórios git conhecidos (pastas irmãs do Mind) e mostra, pra cada um, se tem
mudança não commitada e/ou commit não empurrado. Sob demanda, não é um daemon.

Uso: mind.py status
Repo novo entra na lista REPOS abaixo.
"""
from .common import ROOT
from .platform_ import run

PROJECTS_ROOT = ROOT.parent

# Preencha com os nomes das pastas (irmãs deste vault) que você quer monitorar:
# geralmente o próprio vault do Mind e os repos de projeto ativos.
REPOS = [
    # "mind",
    # "meu-projeto",
]


def git(d, *a):
    return run(["git", "-C", str(d), *a])


def main(args) -> int:
    for name in REPOS:
        d = PROJECTS_ROOT / name
        if not (d / ".git").exists():
            continue
        dirty = "mudanças não commitadas" if git(d, "status", "--porcelain").stdout.strip() else ""
        ahead = ""
        branch = git(d, "symbolic-ref", "--short", "HEAD").stdout.strip()
        if branch:
            if git(d, "rev-parse", "--abbrev-ref", "@{upstream}").returncode == 0:
                count = git(d, "rev-list", "--count", "@{upstream}..HEAD").stdout.strip()
                if count.isdigit() and int(count) > 0:
                    ahead = f"{count} commit(s) não empurrado(s)"
            else:
                ahead = "sem upstream configurado"
        if dirty or ahead:
            print(f"{name:<24} {dirty or '-'} | {ahead or '-'}")
    return 0
