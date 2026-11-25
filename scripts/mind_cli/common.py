"""Pedaços compartilhados: raiz do vault, regra de pastas ignoradas e utilitários de texto."""
import os
import sys
import unicodedata
from pathlib import Path

# scripts/mind_cli/common.py -> raiz do vault
ROOT = Path(__file__).resolve().parents[2]

# Mesma regra do MindView: ignora pastas ocultas e estas.
SKIP_DIRS = {".git", "node_modules", ".obsidian", ".trash", "venv", "__pycache__"}


def setup_stdio() -> None:
    """Força UTF-8 na saída: o console do Windows usa cp1252 e quebra com acento."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def posix(path: str) -> str:
    """Caminho com '/', igual em qualquer sistema (pra comparar e imprimir)."""
    return path.replace(os.sep, "/")


def walk_files(root, skip_hidden_files: bool = True):
    """Gera caminhos relativos (com '/') de todos os arquivos do vault, na regra do MindView."""
    root = str(root)
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not x.startswith("."))
        for f in sorted(files):
            if skip_hidden_files and f.startswith("."):
                continue
            yield posix(os.path.relpath(os.path.join(d, f), root))


def fold(s: str) -> str:
    """Minúscula e sem acento, pra busca."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn"
    )


def read_text(path) -> str:
    with open(path, encoding="utf-8", errors="ignore", newline=None) as fh:
        return fh.read()
