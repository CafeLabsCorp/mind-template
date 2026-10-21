#!/usr/bin/env bash
# Busca um termo no vault inteiro (conteúdo e nome de arquivo), sem diferenciar maiúscula nem acento.
# Mesma regra de pastas do MindView: ignora ocultas e .git/node_modules/.obsidian/.trash/venv/__pycache__.
# Uso: scripts/buscar.sh [-n MAX] termo [mais palavras: a busca é pela frase inteira]   (padrão: 15 arquivos)
# Saída: um arquivo por linha, do que mais cita ao que menos cita, com a 1ª linha onde aparece. Código 1 se nada achar.
# Local e sem custo: quem usa lê só essa saída curta, nunca o vault.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 -I - "$ROOT" "$@" <<'PY'
import os, sys, unicodedata
root, args = sys.argv[1], sys.argv[2:]
limit = 15
if args[:1] == ['-n'] and len(args) > 2:
    limit, args = int(args[1]), args[2:]
if not args:
    sys.exit('uso: scripts/buscar.sh [-n MAX] termo')
fold = lambda s: ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
term = fold(' '.join(args))
SKIP = {'.git', 'node_modules', '.obsidian', '.trash', 'venv', '__pycache__'}
TEXT = {'.md', '.txt', '.sh', '.json', '.mjs', '.js', '.py', '.yml', '.yaml', '.csv', '.html'}
found = []
for d, ds, fs in os.walk(root):
    ds[:] = [x for x in ds if x not in SKIP and not x.startswith('.')]
    for f in fs:
        if f.startswith('.'):
            continue
        path = os.path.join(d, f)
        rel = os.path.relpath(path, root)
        hits, first = 0, ''
        if os.path.splitext(f)[1].lower() in TEXT:
            try:
                for line in open(path, encoding='utf8', errors='ignore'):
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
    sys.exit(1)
found.sort(key=lambda x: (-x[0], x[1]))
for _, rel, hits, by_name, first in found[:limit]:
    tag = f'{hits}x' if hits else 'nome'
    print(f'{rel}  [{tag}{", nome" if hits and by_name else ""}]' + (f'  {first[:140]}' if first else ''))
if len(found) > limit:
    print(f'... e mais {len(found) - limit} arquivos (use -n {len(found)} pra ver todos)')
PY
