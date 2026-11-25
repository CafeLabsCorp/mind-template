"""Cria/recria os symlinks entre mind/claude-user/ e ~/.claude/, pra que as Skills, os Subagentes
e o CLAUDE.md de nível usuário sejam lidos pelo Claude Code a partir do conteúdo versionado aqui.
Rodar uma vez por máquina, depois de um `git clone` (docs/ARQUITETURA.md, seção 6). Idempotente.

Uso: mind.py setup [--target PASTA]   (padrão: ~/.claude; MIND_CLAUDE_HOME também serve)
"""
import os
import shutil
import sys
from pathlib import Path

from .common import ROOT
from .platform_ import IS_WINDOWS, claude_home, make_symlink, remove_link


def link(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink():
        remove_link(dest)
    elif dest.exists():
        print(f"AVISO: {dest} já existe e não é um symlink — pulando. "
              "Mova/apague manualmente e rode de novo se quiser linkar.", file=sys.stderr)
        return
    make_symlink(src, dest)
    print(f"linkado: {dest} -> {src}")


def main(args) -> int:
    target = claude_home()
    if "--target" in args:
        target = Path(args[args.index("--target") + 1])

    print(f"Sistema: {'Windows' if IS_WINDOWS else sys.platform} · Python {sys.version.split()[0]} · "
          f"vault: {ROOT} · destino: {target}")
    if not shutil.which("git"):
        print("AVISO: git não encontrado no PATH.", file=sys.stderr)
    if not shutil.which("rclone"):
        print("AVISO: rclone não encontrado (só o drive-sync precisa dele).", file=sys.stderr)

    cu = ROOT / "claude-user"
    link(cu / "CLAUDE.md", target / "CLAUDE.md")
    # Aponta pra raiz do vault, pra o CLAUDE.md de usuário achar persona.md e config.md de qualquer
    # projeto, sem caminho fixo (docs/ARQUITETURA.md, "Persona espelho").
    link(ROOT, target / "mind-vault")
    if (cu / "skills").is_dir():
        for s in sorted(p for p in (cu / "skills").iterdir() if p.is_dir()):
            link(s, target / "skills" / s.name)
    if (cu / "agents").is_dir():
        for a in sorted((cu / "agents").glob("*.md")):
            link(a, target / "agents" / a.name)
    print("Concluído.")
    return 0
