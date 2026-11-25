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


def documents_dir() -> Path:
    """Pasta Documentos do sistema (no Windows pode estar redirecionada, ex.: OneDrive)."""
    if IS_WINDOWS:
        try:
            import ctypes
            import uuid
            from ctypes import byref, c_ubyte, c_ulong, c_ushort, c_wchar_p

            class GUID(ctypes.Structure):
                _fields_ = [("a", c_ulong), ("b", c_ushort), ("c", c_ushort), ("d", c_ubyte * 8)]

            u = uuid.UUID("FDD39AD0-238F-46AF-ADB4-6C85480369C7")  # FOLDERID_Documents
            g = GUID(u.time_low, u.time_mid, u.time_hi_version, (c_ubyte * 8)(*u.bytes[8:]))
            ptr = c_wchar_p()
            if ctypes.windll.shell32.SHGetKnownFolderPath(byref(g), 0, None, byref(ptr)) == 0:
                path = ptr.value
                ctypes.windll.ole32.CoTaskMemFree(ptr)
                if path:
                    return Path(path)
        except Exception:
            pass
    elif sys.platform != "darwin":
        r = run(["xdg-user-dir", "DOCUMENTS"])
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip())
    return Path.home() / "Documents"


def pin_folder(path: Path) -> str:
    """Fixa a pasta no acesso rápido do sistema. Devolve uma mensagem do que aconteceu."""
    if IS_WINDOWS:
        q = str(path).replace("'", "''")
        r = run(["powershell", "-NoProfile", "-Command",
                 f"(New-Object -ComObject shell.application).Namespace('{q}').Self.InvokeVerb('pintohome')"])
        if r.returncode == 0:
            return "Fixada no Acesso rápido do Explorer."
        return "Não consegui fixar sozinho; no Explorer: clique direito na pasta > Fixar no Acesso rápido."
    if sys.platform == "darwin":
        return "No macOS: arraste a pasta pra barra lateral do Finder (ou Finder > Ir > Ir para a pasta)."
    bm = Path.home() / ".config" / "gtk-3.0" / "bookmarks"
    line = f"{path.as_uri()} {path.name}"
    try:
        bm.parent.mkdir(parents=True, exist_ok=True)
        cur = bm.read_text(encoding="utf-8") if bm.is_file() else ""
        if path.as_uri() not in cur:
            sep = "" if (not cur or cur.endswith(chr(10))) else chr(10)
            bm.write_text(cur + sep + line + chr(10), encoding="utf-8")
        return "Adicionada aos favoritos do gerenciador de arquivos (GTK)."
    except OSError:
        return "Não consegui fixar sozinho; adicione a pasta aos favoritos do seu gerenciador de arquivos."
