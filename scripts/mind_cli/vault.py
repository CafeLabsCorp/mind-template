"""Varredura completa do vault, rodada toda semana na manutenção (docs/ARQUITETURA.md, seção 11).

Só lê e reporta — nunca move nem apaga. Seções: projetos dentro do vault, binários (GitHub/Drive),
duplicados (arquivo e parágrafo), boards de tarefas, READMEs que viraram diário, nós grandes e órfãos.
Uso: mind.py vault [raiz-do-vault]   (padrão: a raiz deste repo)
"""
import collections
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

from . import orfaos, tamanho
from .common import SKIP_DIRS, posix, read_text
from .common import ROOT as DEFAULT_ROOT

BIN = {"png", "jpg", "jpeg", "gif", "webp", "ico", "pdf", "mp4", "mov", "mkv", "webm", "mp3", "wav",
       "m4a", "zip", "ttf", "otf", "woff", "woff2", "docx", "xlsx", "pptx", "psd", "fig"}
CODE = {"html", "js", "mjs", "cjs", "ts", "tsx", "jsx", "css", "py", "sh"}
BUILD = {"package.json", "build.mjs", "vite.config.js", "remotion.config.ts", "render.sh", "Makefile",
         "requirements.txt"}
ENGINE = ("scripts", "claude-user", "docs", ".claude")


def main(args) -> int:
    root = Path(args[0]).resolve() if args else DEFAULT_ROOT
    files, nm_dirs = [], []
    for d, ds, fs in os.walk(root):
        if "node_modules" in ds:
            nm_dirs.append(posix(os.path.relpath(os.path.join(d, "node_modules"), root)))
        ds[:] = [x for x in ds if x not in SKIP_DIRS and not x.startswith(".")]
        for f in fs:
            if not f.startswith("."):
                files.append(posix(os.path.relpath(os.path.join(d, f), root)))

    def ext(p):
        b = p.rsplit("/", 1)[-1]
        return b.rsplit(".", 1)[-1].lower() if "." in b else ""

    size = lambda p: os.path.getsize(root / p)  # noqa: E731
    mb = lambda n: f"{n / 1048576:.1f} MB"  # noqa: E731

    def top(p, depth=2):
        parts = p.split("/")
        return "/".join(parts[: min(depth, len(parts) - 1)]) or "."

    def section(t):
        print(f"\n## {t}")

    def is_engine(p):
        return p.split("/")[0] in ENGINE

    section("Possíveis projetos dentro do vault (viram repo próprio + nó-ponte)")
    cand = collections.defaultdict(lambda: {"build": set(), "code": 0, "bin": 0})
    for p in files:
        if is_engine(p):
            continue
        k = top(p)
        if p.rsplit("/", 1)[-1] in BUILD:
            cand[k]["build"].add(p.rsplit("/", 1)[-1])
        e = ext(p)
        if e in CODE:
            cand[k]["code"] += 1
        if e in BIN:
            cand[k]["bin"] += size(p)
    for n in nm_dirs:
        if not is_engine(n):
            cand[top(n)]["build"].add("node_modules")
    hits = [(k, v) for k, v in cand.items() if v["build"] or v["code"] >= 5]
    for k, v in sorted(hits, key=lambda kv: -kv[1]["code"]):
        extra = f', build: {", ".join(sorted(v["build"]))}' if v["build"] else ""
        print(f'- {k}: {v["code"]} arquivo(s) de código, {mb(v["bin"])} de binário{extra}')
    if not hits:
        print("- nenhum")

    bins = [p for p in files if ext(p) in BIN]
    ign = set()
    if bins:
        # bytes e separador NUL: em modo texto o Windows trocaria "\n" por "\r\n" e o git não casaria
        r = subprocess.run(["git", "-C", str(root), "check-ignore", "-z", "--stdin"],
                           input="\0".join(bins).encode("utf-8"), capture_output=True)
        ign = set(r.stdout.decode("utf-8", errors="replace").split("\0"))
    section("Binários no GitHub (versionados, ou fora do .gitignore): tirar com git rm --cached")
    leak = [p for p in bins if p not in ign]
    for p in leak:
        print(f"- {p} ({mb(size(p))})")
    if not leak:
        print("- nenhum")
    section("Binários por pasta (só no disco: precisam de cópia no Drive)")
    by = collections.Counter()
    for p in bins:
        by[top(p)] += size(p)
    for k, n in by.most_common(15):
        print(f"- {k}: {mb(n)}")
    print(f"- total: {mb(sum(by.values()))} em {len(bins)} arquivo(s)")

    section("Arquivos idênticos (mesmo conteúdo)")
    h = collections.defaultdict(list)
    for p in files:
        if size(p) > 0:
            with open(root / p, "rb") as fh:
                h[hashlib.sha1(fh.read()).hexdigest()].append(p)
    dups = [v for v in h.values() if len(v) > 1]
    for v in dups:
        print("- " + "  =  ".join(v))
    if not dups:
        print("- nenhum")

    section("Parágrafos repetidos em mais de um nó (possível fato duplicado)")
    mds = [p for p in files if p.endswith(".md") and not is_engine(p) and p != "CHANGELOG.md"]
    para = collections.defaultdict(set)
    for p in mds:
        for b in re.split(r"\n\s*\n", read_text(root / p)):
            n = re.sub(r"\s+", " ", re.sub(r"[`*_>#\[\]()-]", "", b)).strip().lower()
            if len(n) >= 160:
                para[n].add(p)
    rep = sorted((sorted(v), k) for k, v in para.items() if len(v) > 1)
    for v, k in rep[:30]:
        print(f'- {"  |  ".join(v)} — "{k[:90]}…"')
    if len(rep) > 30:
        print(f"- … e mais {len(rep) - 30}")
    if not rep:
        print("- nenhum")

    section("Boards de tarefas (feitos x abertos)")
    for p in sorted(x for x in mds if x.startswith("tarefas/")):
        t = read_text(root / p)
        d = len(re.findall(r"^\s*- \[x\]", t, re.M | re.I))
        a = len(re.findall(r"^\s*- \[ \]", t, re.M))
        if d:
            print(f"- {p}: {d} feito(s), {a} aberto(s)")

    section("Tarefas (formato do board)")
    from . import tarefas
    tarefas.report(root)

    section("README de pasta longo (índice que pode ter virado diário)")
    long = []
    for p in mds:
        if p.rsplit("/", 1)[-1] == "README.md" and "/" in p:
            n = read_text(root / p).count("\n") + 1
            if n > 60:
                long.append((n, p))
    for n, p in sorted(long, reverse=True):
        print(f"- {p}: {n} linhas")
    if not long:
        print("- nenhum")

    print("\n## Nós acima do limite de split", flush=True)
    tamanho.main(["150", str(root)])
    sys.stdout.flush()
    print("\n## Órfãos (nenhum .md linka)", flush=True)
    orfaos.main([str(root)])
    sys.stdout.flush()
    return 0
