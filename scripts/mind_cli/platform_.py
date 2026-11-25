"""Tudo que muda de um sistema pra outro fica aqui (e só aqui)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

IS_WINDOWS = os.name == "nt"
SYSTEM = "windows" if IS_WINDOWS else ("macos" if sys.platform == "darwin" else "linux")


def claude_home() -> Path:
    """Pasta ~/.claude (ou MIND_CLAUDE_HOME, pra testar sem mexer na real)."""
    env = os.environ.get("MIND_CLAUDE_HOME")
    return Path(env) if env else Path.home() / ".claude"


def make_symlink(src: Path, dest: Path) -> None:
    """Cria symlink. No Windows, exige Modo Desenvolvedor (ou admin); explica se faltar."""
    try:
        os.symlink(src, dest, target_is_directory=src.is_dir())
    except OSError as e:
        if IS_WINDOWS and getattr(e, "winerror", None) == 1314:
            raise SystemExit(
                "O Windows negou criar o link (falta permissão de symlink).\n"
                "Ligue o Modo Desenvolvedor: Configurações > Sistema > Para desenvolvedores >\n"
                "Modo Desenvolvedor. Depois rode o setup de novo."
            )
        raise


def remove_link(path: Path) -> None:
    try:
        os.unlink(path)
    except (PermissionError, IsADirectoryError):
        os.rmdir(path)  # symlink de pasta no Windows


def find_browser() -> str:
    """Acha Chrome, Edge ou Chromium pra imprimir PDF."""
    candidates = []
    if IS_WINDOWS:
        for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"),
                     os.environ.get("LOCALAPPDATA")):
            if not base:
                continue
            candidates += [
                os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe"),
            ]
    elif sys.platform == "darwin":
        candidates += [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    for name in ("google-chrome", "google-chrome-stable", "chromium-browser", "chromium",
                 "microsoft-edge", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            candidates.append(found)
    candidates.append("/snap/bin/chromium")
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    raise SystemExit("Nenhum Chrome, Edge ou Chromium encontrado.")


def run(cmd, **kw) -> subprocess.CompletedProcess:
    """subprocess.run com texto em UTF-8, igual nos dois sistemas."""
    kw.setdefault("capture_output", True)
    kw.setdefault("text", True)
    kw.setdefault("encoding", "utf-8")
    kw.setdefault("errors", "replace")
    return subprocess.run(cmd, **kw)


def npx_command(args) -> list:
    """Comando pra rodar um pacote via npx. No Windows nativo o npx é um .cmd, então precisa do `cmd /c`."""
    return (["cmd", "/c", "npx"] if IS_WINDOWS else ["npx"]) + list(args)
