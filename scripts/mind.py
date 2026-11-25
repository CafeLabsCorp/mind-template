#!/usr/bin/env python3
"""Ponto de entrada dos utilitários do Mind (Windows, Linux e macOS, só biblioteca padrão).

Uso: python scripts/mind.py <comando> [argumentos]
Lista de comandos: python scripts/mind.py --help
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mind_cli.main import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
