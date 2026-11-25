"""Espelha os binários do vault (ou de um repo de projeto) no Drive, via rclone.

O GitHub só leva texto; binário fica no disco e tem cópia no Drive, na mesma árvore de pastas.
O que conta como binário vem do .gitignore da pasta (fonte única): as linhas "*.ext" e as linhas
com caminho que terminam em "/" ou "*.ext" (ex.: "marca/*/png/", "contratos/*.pdf").
Pastas "out/" (vídeo/imagem renderizados, que se gera de novo a partir do código) nunca sobem.
Sempre "rclone copy" (nunca "sync"): nada é apagado de nenhum dos lados.
No pull entra "--immutable": o Drive nunca sobrescreve um arquivo local que já existe e difere.

Uso: mind.py drive push|pull [pasta-local] [remote:caminho] [--dry-run]
  push  disco -> Drive (rodar depois de guardar arquivo novo)
  pull  Drive -> disco (máquina nova: clonar, configurar o rclone, rodar o pull)
  padrão: a raiz deste vault e $MIND_DRIVE_REMOTE (ou gdrive:mind)
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .common import ROOT


def build_filters(gitignore: Path):
    """Regras do rclone em ordem: pastas fora, cada extensão dentro, e todo o resto fora."""
    lines = gitignore.read_text(encoding="utf-8").splitlines()
    flt = []
    for d in (".git", "node_modules", "out", ".obsidian", ".trash", ".claude"):
        flt += ["--filter", f"- {d}/**"]
    n = 0
    exts = sorted({m.group(1) for l in lines if (m := re.fullmatch(r"\*\.([A-Za-z0-9]+)", l.strip()))})
    for e in exts:
        flt += ["--filter", f"+ *.{e}", "--filter", f"+ *.{e.upper()}"]
        n += 1
    paths = sorted({
        l.strip() for l in lines
        if l.strip() and not l.startswith(("#", "!")) and "/" in l
        and re.search(r"(/|\*\.[A-Za-z0-9]+)$", l.strip())
        and not re.search(r"(^|/)(node_modules|build)/", l.strip())
    })
    for pat in paths:
        pat = "/" + pat.lstrip("/")
        if pat.endswith("/"):
            pat += "**"
        flt += ["--filter", f"+ {pat}"]
        n += 1
    if n == 0:
        raise SystemExit(f"nenhum padrão binário ('*.ext' ou caminho) em {gitignore}")
    flt += ["--filter", "- *"]
    return flt


def main(args) -> int:
    if not args or args[0] not in ("push", "pull"):
        print(__doc__)
        return 2
    mode, rest = args[0], args[1:]
    dry = ["--dry-run"] if "--dry-run" in rest else []
    pos = [a for a in rest if a != "--dry-run"]
    local = Path(pos[0]).resolve() if pos else ROOT
    remote = pos[1] if len(pos) > 1 else os.environ.get("MIND_DRIVE_REMOTE", "gdrive:mind")

    rclone = shutil.which("rclone")
    if not rclone:
        raise SystemExit("rclone não instalado (ver claude-user/CLAUDE.md, regra de binários)")
    remotes = subprocess.run([rclone, "listremotes"], capture_output=True, text=True).stdout.split()
    if remote.split(":")[0] + ":" not in remotes:
        raise SystemExit(f"remote '{remote.split(':')[0]}' não configurado: rode 'rclone config'")

    gi = local / ".gitignore"
    if not gi.is_file():
        gi = ROOT / ".gitignore"
    flt = build_filters(gi)
    src, dst = (str(local), remote) if mode == "push" else (remote, str(local))
    print(f"{mode}: {src} -> {dst}", flush=True)
    # No pull o Drive nunca sobrescreve um arquivo local que já existe e difere (--immutable);
    # no push a versão nova do disco tem que atualizar o Drive, então ali não vale.
    safe = ["--immutable"] if mode == "pull" else []
    code = subprocess.call([rclone, "copy", src, dst, *flt, *safe, *dry, "--stats-one-line", "--stats", "10s", "-P"])
    if code != 0 and mode == "pull":
        print(chr(10) + "Se o rclone apontou arquivo que 'differs', ficou o seu local (o pull não sobrescreve). "
              "Pra conferir o que mudou: mind.py drive push --dry-run.")
    return code
