"""Pasta de saída do Mind: onde cai tudo que o Claude gera pra você ver ou usar (imagem, vídeo, logo, PDF, render).

Uso:
  mind.py output                    mostra o caminho da pasta e cria se faltar
  mind.py output --fixar            também fixa no acesso rápido (Windows e Linux; no macOS mostra o passo manual)
  mind.py output lista [--antigos N]  lista o que tem mais de N dias (padrão 30); só lista, nunca apaga

O caminho vem do `config.md` (pergunta "Pasta de saída"); sem resposta, usa `output-mind` dentro da pasta Documentos
do sistema. A pasta fica FORA do vault, então não vai pro git nem pro Drive.
"""
import re
import sys
import time
from pathlib import Path

from .common import ROOT, read_text
from .platform_ import documents_dir, pin_folder

DEFAULT_NAME = "output-mind"


def output_dir() -> Path:
    cfg = ROOT / "config.md"
    if cfg.is_file():
        m = re.search(r"^## Pasta de saída\s*\n(.*?)(?=^## |\Z)", read_text(cfg), re.M | re.S)
        if m:
            a = re.search(r"\*\*Resposta:\*\*\s*(.+)", m.group(1))
            if a:
                val = a.group(1).strip().strip("`").strip()
                if val and not val.startswith("("):  # "(padrão)" ou "(ainda não respondido)" = usar o padrão
                    return Path(val).expanduser()
    return documents_dir() / DEFAULT_NAME


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def cmd_lista(out: Path, days: int) -> int:
    if not out.is_dir():
        print(f"A pasta de saída ainda não existe: {out}")
        return 0
    limit = time.time() - days * 86400
    old, total = [], 0
    for p in out.rglob("*"):
        if p.is_file():
            total += 1
            if p.stat().st_mtime < limit:
                old.append(p)
    old.sort(key=lambda p: p.stat().st_mtime)
    print(f"# Pasta de saída: {out}\n  {total} arquivo(s); {len(old)} com mais de {days} dias\n")
    size = 0
    for p in old:
        st = p.stat()
        size += st.st_size
        age = int((time.time() - st.st_mtime) / 86400)
        print(f"  {age:>4} d  {human(st.st_size):>9}  {p.relative_to(out).as_posix()}")
    if old:
        print(f"\n  total: {human(size)}. Nada foi apagado; a limpeza só acontece com o sim da pessoa.")
    return 0


def main(args) -> int:
    if args and args[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    out = output_dir()
    if args and args[0] == "lista":
        days = 30
        if "--antigos" in args:
            try:
                days = int(args[args.index("--antigos") + 1])
            except (IndexError, ValueError):
                print("use: lista --antigos <dias>", file=sys.stderr)
                return 2
        return cmd_lista(out, days)
    if args and args[0] not in ("--fixar",):
        print(f"argumento desconhecido: {args[0]} (use --fixar ou lista)", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    print(out)
    if "--fixar" in args:
        print(pin_folder(out))
    return 0
