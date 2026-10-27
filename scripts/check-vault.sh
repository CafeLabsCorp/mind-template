#!/usr/bin/env bash
# Varredura completa do vault, rodada toda semana na manutenção (docs/ARQUITETURA.md, seção 11).
# Só lê e reporta — nunca move nem apaga. O agente de manutenção usa a saída pra saber onde ler a fundo.
# Seções: projetos dentro do vault, binários (GitHub/Drive), duplicados (arquivo e parágrafo),
# boards de tarefas, READMEs que viraram diário, nós grandes e órfãos.
# Uso: scripts/check-vault.sh [raiz-do-vault]   (padrão: a raiz deste repo)
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
DIR="$(cd "$(dirname "$0")" && pwd)"
python3 -I - "$ROOT" <<'PY'
import os, re, sys, hashlib, subprocess, collections
root = sys.argv[1]
SKIP = {'.git', 'node_modules', '.obsidian', '.trash', 'venv', '__pycache__'}
BIN = {'png','jpg','jpeg','gif','webp','ico','pdf','mp4','mov','mkv','webm','mp3','wav','m4a',
       'zip','ttf','otf','woff','woff2','docx','xlsx','pptx','psd','fig'}
CODE = {'html','js','mjs','cjs','ts','tsx','jsx','css','py','sh'}
BUILD = {'package.json','build.mjs','vite.config.js','remotion.config.ts','render.sh','Makefile','requirements.txt'}

files, nm_dirs = [], []
for d, ds, fs in os.walk(root):
    if 'node_modules' in ds:
        nm_dirs.append(os.path.relpath(os.path.join(d, 'node_modules'), root))
    ds[:] = [x for x in ds if x not in SKIP and not x.startswith('.')]
    for f in fs:
        if not f.startswith('.'):
            files.append(os.path.relpath(os.path.join(d, f), root))
ext = lambda p: p.rsplit('.', 1)[-1].lower() if '.' in os.path.basename(p) else ''
size = lambda p: os.path.getsize(os.path.join(root, p))
mb = lambda n: f'{n/1048576:.1f} MB'
def top(p, depth=2):
    parts = p.split(os.sep)
    return os.sep.join(parts[:min(depth, len(parts) - 1)]) or '.'
ENGINE = ('scripts', 'claude-user', 'docs', '.claude')
def section(t): print(f'\n## {t}')

# 1. Projetos dentro do vault (regra "conhecimento vs. projeto")
section('Possíveis projetos dentro do vault (viram repo próprio + nó-ponte)')
cand = collections.defaultdict(lambda: {'build': set(), 'code': 0, 'bin': 0})
for p in files:
    if p.startswith(ENGINE):
        continue
    k = top(p)
    if os.path.basename(p) in BUILD:
        cand[k]['build'].add(os.path.basename(p))
    e = ext(p)
    if e in CODE: cand[k]['code'] += 1
    if e in BIN: cand[k]['bin'] += size(p)
for n in nm_dirs:
    if not n.startswith(ENGINE):
        cand[top(n)]['build'].add('node_modules')
hits = [(k, v) for k, v in cand.items() if v['build'] or v['code'] >= 5]
for k, v in sorted(hits, key=lambda kv: -kv[1]['code']):
    print(f'- {k}: {v["code"]} arquivo(s) de código, {mb(v["bin"])} de binário' + (f', build: {", ".join(sorted(v["build"]))}' if v['build'] else ''))
if not hits: print('- nenhum')

# 2. Binários
bins = [p for p in files if ext(p) in BIN]
ign = set()
if bins:
    r = subprocess.run(['git', '-C', root, 'check-ignore', '--stdin'], input='\n'.join(bins), capture_output=True, text=True)
    ign = set(r.stdout.split('\n'))
section('Binários no GitHub (versionados, ou fora do .gitignore): tirar com git rm --cached')
leak = [p for p in bins if p not in ign]
for p in leak: print(f'- {p} ({mb(size(p))})')
if not leak: print('- nenhum')
section('Binários por pasta (só no disco: precisam de cópia no Drive)')
by = collections.Counter()
for p in bins: by[top(p)] += size(p)
for k, n in by.most_common(15): print(f'- {k}: {mb(n)}')
print(f'- total: {mb(sum(by.values()))} em {len(bins)} arquivo(s)')

# 3. Duplicados
section('Arquivos idênticos (mesmo conteúdo)')
h = collections.defaultdict(list)
for p in files:
    if size(p) > 0:
        h[hashlib.sha1(open(os.path.join(root, p), 'rb').read()).hexdigest()].append(p)
dups = [v for v in h.values() if len(v) > 1]
for v in dups: print('- ' + '  =  '.join(v))
if not dups: print('- nenhum')
section('Parágrafos repetidos em mais de um nó (possível fato duplicado)')
mds = [p for p in files if p.endswith('.md') and not p.startswith(ENGINE) and p != 'CHANGELOG.md']
para = collections.defaultdict(set)
for p in mds:
    t = open(os.path.join(root, p), encoding='utf8', errors='ignore').read()
    for b in re.split(r'\n\s*\n', t):
        n = re.sub(r'\s+', ' ', re.sub(r'[`*_>#\[\]()-]', '', b)).strip().lower()
        if len(n) >= 160:
            para[n].add(p)
rep = sorted((sorted(v), k) for k, v in para.items() if len(v) > 1)
for v, k in rep[:30]: print(f'- {"  |  ".join(v)} — "{k[:90]}…"')
if len(rep) > 30: print(f'- … e mais {len(rep) - 30}')
if not rep: print('- nenhum')

# 4. Boards
section('Boards de tarefas (feitos x abertos)')
for p in sorted(x for x in mds if x.startswith('tarefas' + os.sep)):
    t = open(os.path.join(root, p), encoding='utf8', errors='ignore').read()
    d, a = len(re.findall(r'^\s*- \[x\]', t, re.M | re.I)), len(re.findall(r'^\s*- \[ \]', t, re.M))
    if d: print(f'- {p}: {d} feito(s), {a} aberto(s)')

# 5. READMEs que viraram diário
section('README de pasta longo (índice que pode ter virado diário)')
long = [(sum(1 for _ in open(os.path.join(root, p), encoding='utf8', errors='ignore')), p)
        for p in mds if os.path.basename(p) == 'README.md' and os.sep in p]
long = sorted((x for x in long if x[0] > 60), reverse=True)
for n, p in long: print(f'- {p}: {n} linhas')
if not long: print('- nenhum')
PY
echo; echo "## Nós acima do limite de split"
bash "$DIR/check-tamanho.sh" 150 "$ROOT" 2>&1 || true
echo; echo "## Órfãos (nenhum .md linka)"
bash "$DIR/check-orfaos.sh" "$ROOT" 2>&1 | tail -n 40 || true
