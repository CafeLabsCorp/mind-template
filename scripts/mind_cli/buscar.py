"""Busca um termo no vault inteiro (conteúdo e nome de arquivo), sem diferenciar maiúscula nem acento.

Uso: mind.py buscar [-n MAX] termo [mais palavras: a busca é pela frase inteira]   (padrão: 15 arquivos)
Saída: um arquivo por linha, do que mais cita ao que menos cita, com a 1ª linha onde aparece.
Código 1 se nada achar. Local e sem custo: quem usa lê só essa saída curta, nunca o vault.
"""
import os
import sys

from .common import ROOT, fold, walk_files

TEXT = {".md", ".txt", ".sh", ".json", ".mjs", ".js", ".py", ".yml", ".yaml", ".csv", ".html"}


def main(args) -> int:
    limit = 15
    if args[:1] == ["-n"] and len(args) > 2:
        limit, args = int(args[1]), args[2:]
    if not args:
        print("uso: mind.py buscar [-n MAX] termo", file=sys.stderr)
        return 2
    term = fold(" ".join(args))
    found = []
    for rel in walk_files(ROOT):
        hits, first = 0, ""
        if os.path.splitext(rel)[1].lower() in TEXT:
            try:
                with open(ROOT / rel, encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        n = fold(line).count(term)
                        if n:
                            hits += n
                            first = first or line.strip()
            except OSError:
                continue
        by_name = term in fold(rel)
        if hits or by_name:
            found.append((hits + (100 if by_name else 0), rel, hits, by_name, first))
    if not found:
        print(f'nada achado para «{" ".join(args)}»')
        return 1
    found.sort(key=lambda x: (-x[0], x[1]))
    for _, rel, hits, by_name, first in found[:limit]:
        tag = f"{hits}x" if hits else "nome"
        print(f'{rel}  [{tag}{", nome" if hits and by_name else ""}]' + (f"  {first[:140]}" if first else ""))
    if len(found) > limit:
        print(f"... e mais {len(found) - limit} arquivos (use -n {len(found)} pra ver todos)")
    return 0
