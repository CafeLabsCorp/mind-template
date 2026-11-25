"""Mostra quais ferramentas do Mind estão instaladas nesta máquina e como instalar o que falta.

Uso:
  mind.py ferramentas                      lista o que está instalado e o que falta (com a dica do seu sistema)
  mind.py ferramentas devtools             mostra o comando que registra o chrome-devtools no `claude`
  mind.py ferramentas devtools --aplicar   roda esse comando (só com o sim de quem usa; reinicie o Claude depois)

O registro das ferramentas (pra que serve cada uma, quando preferir) está em `docs/ferramentas.md`.
Só leitura, exceto `devtools --aplicar`, que mexe só no registro de MCP do `claude` em escopo de usuário.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from .platform_ import SYSTEM, npx_command

# nome, binário, o que é, dica por sistema, obrigatório pro Mind?
TOOLS = [
    ("Python", ["python", "python3"], "roda o engine do Mind", True, {
        "windows": "winget install Python.Python.3.12",
        "macos": "brew install python",
        "linux": "pacote da distro (python3)"}),
    ("Git", ["git"], "versiona o vault", True, {
        "windows": "winget install Git.Git",
        "macos": "brew install git",
        "linux": "pacote da distro (git)"}),
    ("Claude Code (CLI)", ["claude"], "registra MCP e roda as sessões", False, {
        "windows": "veja claude.com/code",
        "macos": "veja claude.com/code",
        "linux": "veja claude.com/code"}),
    ("Node", ["node"], "necessário pro chrome-devtools e pra projetos web", False, {
        "windows": "winget install OpenJS.NodeJS.LTS",
        "macos": "brew install node",
        "linux": "pacote da distro ou nvm"}),
    ("rclone", ["rclone"], "espelha arquivos pesados no Drive (`mind.py drive`)", False, {
        "windows": "winget install Rclone.Rclone",
        "macos": "brew install rclone",
        "linux": "pacote da distro ou o script de rclone.org/install"}),
    ("ffmpeg", ["ffmpeg"], "áudio e vídeo", False, {
        "windows": "winget install Gyan.FFmpeg",
        "macos": "brew install ffmpeg",
        "linux": "pacote da distro (ffmpeg)"}),
]


def which_any(names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return ""


def mcp_registered(name: str) -> bool:
    """Lê ~/.claude.json (escopo de usuário e de projeto) e diz se o MCP está registrado."""
    path = Path.home() / ".claude.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if name in (data.get("mcpServers") or {}):
        return True
    return any(name in (proj.get("mcpServers") or {}) for proj in (data.get("projects") or {}).values())


def devtools_command():
    base = ["claude", "mcp", "add", "--scope", "user", "chrome-devtools", "--"]
    return base + npx_command(["-y", "chrome-devtools-mcp@latest"])


def cmd_listar() -> int:
    print(f"# Ferramentas nesta máquina ({SYSTEM})\n")
    missing = []
    for name, bins, what, required, hints in TOOLS:
        found = which_any(bins)
        mark = "ok " if found else ("FALTA" if required else "falta")
        print(f"  [{mark}] {name} — {what}" + (f"  ({found})" if found else ""))
        if not found:
            missing.append((name, hints[SYSTEM], required))
    dev = mcp_registered("chrome-devtools")
    print(f"  [{'ok ' if dev else 'falta'}] chrome-devtools (MCP) — inspeção de páginas: DOM, CSS, console, rede")
    print("  [ ?  ] Claude in Chrome e navegador embutido — não dá pra detectar por script; veja o app")
    if missing or not dev:
        print("\n## Como instalar o que falta")
        for name, hint, required in missing:
            print(f"- {name}{' (obrigatório)' if required else ''}: {hint}")
        if not dev:
            print("- chrome-devtools: `python scripts/mind.py ferramentas devtools` mostra o comando; `--aplicar` registra")
    return 0


def cmd_devtools(apply: bool) -> int:
    cmd = devtools_command()
    print("Comando pro seu sistema:\n  " + " ".join(cmd))
    if not apply:
        print("\nPra registrar de uma vez: python scripts/mind.py ferramentas devtools --aplicar")
        return 0
    if not shutil.which("claude"):
        print("\nO CLI `claude` não está no PATH; registre pelo app ou instale o Claude Code.", file=sys.stderr)
        return 1
    if not shutil.which("node"):
        print("\nAviso: o Node não está instalado; o MCP só funciona depois de instalar (veja a lista).", file=sys.stderr)
    cmd[0] = shutil.which("claude")
    r = subprocess.run(cmd)
    if r.returncode == 0:
        print("\nRegistrado. Reinicie o Claude pra ele aparecer.")
    return r.returncode


def main(args) -> int:
    if args and args[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    if not args:
        return cmd_listar()
    if args[0] == "devtools":
        return cmd_devtools("--aplicar" in args[1:])
    print(f"subcomando desconhecido: {args[0]} (use: devtools)", file=sys.stderr)
    return 2
