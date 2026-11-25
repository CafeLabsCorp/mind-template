"""Lê o board de tarefas (`tarefas/**/*.md`) e responde: o que fazer agora, lista com filtros e checagem de formato.

Uso:
  mind.py tarefas foco                  o que atacar agora (atrasadas, 🔴 prontas, bloqueadas, aguardando)
  mind.py tarefas lista [filtros]       lista tarefas abertas
      --prio vermelho|amarelo|verde     (ou 🔴 🟡 🟢)
      --area <pasta>                    ex.: pessoal, empresa
      --tipo ideia|estudo|aguardando    (padrão: só o que é ação, sem ideias, estudos e aguardando)
      --todas                           inclui ideias, estudos e aguardando
  mind.py tarefas check [--tudo]        valida o formato (IDs, dependências, sem marcador, linha longa, prazo, ideia velha)

A convenção de marcadores está em `tarefas/tarefas.md`; o desenho, em `docs/ARQUITETURA.md`.
Só leitura: nunca edita o board. `check` sai com código 1 se achar erro (ID duplicado ou dependência quebrada).
"""
import re
import sys
from datetime import date, timedelta
from pathlib import Path

from .common import ROOT, read_text, walk_files

ITEM = re.compile(r"^(\s*)- \[( |x|X)\]\s+(.*)$")
PRIO = {"🔴": "alta", "🟡": "média", "🟢": "baixa"}
ISO = r"(\d{4}-\d{2}-\d{2})"
ID_END = re.compile(r"\^([a-z0-9][a-z0-9-]*)\s*$")
DEPENDS = re.compile(r"⛓\s*depende de\s+\^([a-z0-9][a-z0-9-]*)")
DUE = re.compile(r"📅\s*" + ISO)
REVIEWED = re.compile(r"🔁\s*" + ISO)
CREATED = re.compile(r"\(" + ISO + r"\)")
ANY_DATE = re.compile(ISO)
WAIT = re.compile(r"⏳\s*([^^⛓]*)")
TITLE = re.compile(r"\*\*(.+?)\*\*")

MARKERS = re.compile(r"[🔴🟡🟢💡📚]\s*")
MAX_LINE = 300         # acima disso o detalhe deveria estar num nó, com link
IDEA_DAYS = 90          # ideia mais velha que isso entra na pergunta "manter ou descartar"
SOON_DAYS = 7           # prazo que entra no foco


class Task:
    __slots__ = ("file", "area", "line", "done", "text", "prio", "idea", "study", "wait",
                 "due", "created", "reviewed", "id", "deps", "title", "length", "indent")

    def __init__(self, file, area, line, done, text, indent=0):
        self.file, self.area, self.line, self.done, self.text = file, area, line, done, text
        self.indent = indent
        self.length = len(text)
        self.prio = next((p for p in PRIO if p in text), "")
        self.idea = "💡" in text
        self.study = "📚" in text
        w = WAIT.search(text) if "⏳" in text else None
        self.wait = (w.group(1).strip() or "(sem motivo)") if w else ""
        d = DUE.search(text)
        self.due = _date(d.group(1)) if d else None
        r = REVIEWED.search(text)
        self.reviewed = _date(r.group(1)) if r else None
        c = CREATED.search(text)
        if c:
            self.created = _date(c.group(1))
        else:
            others = [m.group(1) for m in ANY_DATE.finditer(REVIEWED.sub("", DUE.sub("", text)))]
            self.created = _date(others[0]) if others else None
        m = ID_END.search(text)
        self.id = m.group(1) if m else ""
        self.deps = DEPENDS.findall(text)
        t = TITLE.search(text)
        raw = t.group(1) if t else MARKERS.sub("", text)
        self.title = raw.strip()[:90]

    @property
    def action(self):
        """Ação de verdade: nem ideia, nem estudo, nem aguardando."""
        return not (self.idea or self.study or self.wait)

    @property
    def idea_since(self):
        """Desde quando a ideia conta: a revisão mais recente (🔁) ou, sem ela, a criação."""
        return max((d for d in (self.created, self.reviewed) if d), default=None)

    @property
    def where(self):
        return f"{self.file}:{self.line}"


def _date(s):
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def load(root: Path = ROOT):
    tasks = []
    for rel in walk_files(root):
        if not (rel.startswith("tarefas/") and rel.endswith(".md")):
            continue
        parts = rel.split("/")
        area = parts[1] if len(parts) > 2 else parts[1][:-3]
        for n, raw in enumerate(read_text(root / rel).splitlines(), 1):
            m = ITEM.match(raw)
            if m:
                tasks.append(Task(rel[len("tarefas/"):], area, n, m.group(2) != " ", m.group(3), len(m.group(1))))
    return tasks


def _fmt(t: Task):
    mark = t.prio or ("💡" if t.idea else "  ")
    extra = f"  ⏳ {t.wait}" if t.wait else ""
    extra += f"  📅 {t.due}" if t.due else ""
    return f"  {mark} [{t.where}] {t.title}{extra}"


# ---------------------------------------------------------------- foco

def cmd_foco(tasks, today):
    open_ = [t for t in tasks if not t.done]
    done_ids = {t.id for t in tasks if t.done and t.id}
    open_ids = {t.id for t in open_ if t.id}

    def blocked_by(t):
        return [d for d in t.deps if d in open_ids and d not in done_ids]

    soon = today + timedelta(days=SOON_DAYS)
    due = sorted((t for t in open_ if t.due and t.due <= soon and not t.wait), key=lambda t: t.due)
    ready = [t for t in open_ if t.prio == "🔴" and t.action and not blocked_by(t) and t not in due]
    blocked = [t for t in open_ if t.prio == "🔴" and t.action and blocked_by(t)]
    waiting = [t for t in open_ if t.wait]

    print(f"# Foco de {today}\n")
    if due:
        print(f"## Prazo até {soon} (ou atrasado)")
        for t in due:
            tag = "ATRASADA" if t.due < today else str(t.due)
            print(f"{_fmt(t)}   <- {tag}")
        print()
    print(f"## 🔴 prontas pra fazer ({len(ready)})")
    for t in ready:
        print(_fmt(t))
    if not ready:
        print("  nenhuma")
    if blocked:
        print(f"\n## 🔴 bloqueadas por dependência ({len(blocked)})")
        for t in blocked:
            print(f"{_fmt(t)}   <- espera ^{', ^'.join(blocked_by(t))}")
    if waiting:
        print(f"\n## ⏳ aguardando ({len(waiting)})")
        for t in waiting:
            print(_fmt(t))
    return 0


# ---------------------------------------------------------------- lista

def _prio_arg(v):
    v = v.lower()
    table = {"vermelho": "🔴", "alta": "🔴", "amarelo": "🟡", "media": "🟡", "média": "🟡",
             "verde": "🟢", "baixa": "🟢", "🔴": "🔴", "🟡": "🟡", "🟢": "🟢"}
    return table.get(v)


def cmd_lista(tasks, args):
    prio = area = tipo = None
    todas = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--todas":
            todas = True
        elif a in ("--prio", "--area", "--tipo") and i + 1 < len(args):
            i += 1
            if a == "--prio":
                prio = _prio_arg(args[i])
                if not prio:
                    print(f"prioridade desconhecida: {args[i]}", file=sys.stderr)
                    return 2
            elif a == "--area":
                area = args[i].lower()
            else:
                tipo = args[i].lower()
        else:
            print(f"argumento desconhecido: {a}", file=sys.stderr)
            return 2
        i += 1

    out = [t for t in tasks if not t.done]
    if prio:
        out = [t for t in out if t.prio == prio]
    if area:
        out = [t for t in out if t.area.lower() == area]
    if tipo:
        keys = {"ideia": lambda t: t.idea, "estudo": lambda t: t.study, "aguardando": lambda t: bool(t.wait)}
        if tipo not in keys:
            print("tipo deve ser ideia, estudo ou aguardando", file=sys.stderr)
            return 2
        out = [t for t in out if keys[tipo](t)]
    elif not todas:
        out = [t for t in out if t.action]
    order = {"🔴": 0, "🟡": 1, "🟢": 2, "": 3}
    out.sort(key=lambda t: (order[t.prio], t.file, t.line))
    for t in out:
        print(_fmt(t))
    print(f"\n{len(out)} tarefa(s)", file=sys.stderr)
    return 0


# ---------------------------------------------------------------- check

def configured_areas(root: Path = ROOT):
    """Áreas respondidas em config.md (pergunta "Áreas de tarefas"); vazio se ainda não respondida."""
    cfg = root / "config.md"
    if not cfg.is_file():
        return []
    m = re.search(r"^## Áreas de tarefas\s*\n(.*?)(?=^## |\Z)", read_text(cfg), re.M | re.S)
    a = re.search(r"\*\*Resposta:\*\*\s*(.+)", m.group(1)) if m else None
    if not a:
        return []
    val = re.sub(r"\(.*?\)", "", a.group(1)).replace("`", "").strip().rstrip(".")
    if not val:
        return []
    return [x.strip().lower() for x in re.split(r"[,;]", val) if x.strip()]


def cmd_check(tasks, today, everything=False, root: Path = ROOT):
    errors, warns = [], []
    open_ = [t for t in tasks if not t.done]

    seen = {}
    for t in tasks:
        if t.id:
            seen.setdefault(t.id, []).append(t)
    for i, ts in sorted(seen.items()):
        if len(ts) > 1:
            errors.append(f"ID duplicado ^{i}: " + ", ".join(t.where for t in ts))

    for t in open_:
        for d in t.deps:
            if d not in seen:
                errors.append(f"{t.where}: ⛓ depende de ^{d}, que não existe")

    no_marker = [t for t in open_ if t.indent == 0 and not (t.prio or t.idea or t.study)]  # sub-item herda do pai
    stale_due = [t for t in open_ if t.due and t.due < today and not t.wait]
    ideas_old = sorted(
        (t for t in open_ if t.idea and t.idea_since and (today - t.idea_since).days > IDEA_DAYS),
        key=lambda t: t.idea_since)
    ideas_nodate = [t for t in open_ if t.idea and not t.created]
    long_ = sorted((t for t in open_ if t.length > MAX_LINE), key=lambda t: -t.length)
    due_no_id = [t for t in open_ if t.due and not t.id]
    no_date = [t for t in open_ if not t.created]

    def block(title, items, fmt, limit=8):
        if not items:
            return
        warns.append(f"{title}: {len(items)}")
        shown = items if everything else items[:limit]
        for t in shown:
            warns.append(f"    {fmt(t)}")
        if len(items) > len(shown):
            warns.append(f"    … e mais {len(items) - len(shown)} (use --tudo)")

    block("📅 vencidas e ainda abertas", stale_due, lambda t: f"{t.where} (venceu {t.due}) {t.title}")
    block("sem marcador (falta 🔴🟡🟢, 💡 ou 📚)", no_marker, lambda t: f"{t.where} {t.title}")
    block(f"💡 com mais de {IDEA_DAYS} dias (manter ou descartar?)", ideas_old,
          lambda t: f"{t.where} ({t.idea_since}) {t.title}")
    block(f"linha com mais de {MAX_LINE} caracteres (mover o detalhe pro nó e deixar o link)", long_,
          lambda t: f"{t.where} ({t.length}) {t.title}")
    block("📅 sem ^id", due_no_id, lambda t: f"{t.where} {t.title}")
    for area in configured_areas(root):
        if not ((root / "tarefas" / f"{area}.md").is_file() or (root / "tarefas" / area).is_dir()):
            warns.append(f"área '{area}' (config.md) sem arquivo nem pasta em tarefas/ (o Claude cria na primeira tarefa)")

    print(f"# Tarefas: {len(open_)} abertas, {len(tasks) - len(open_)} feitas")
    print(f"  sem data de criação: {len(no_date)} (ideias sem data: {len(ideas_nodate)}; elas não envelhecem)")
    print()
    if errors:
        print("## Erros")
        for e in errors:
            print(f"- {e}")
        print()
    if warns:
        print("## Avisos")
        for w in warns:
            print(w if w.startswith("    ") else f"- {w}")
    if not errors and not warns:
        print("Tudo certo.")
    return 1 if errors else 0


def report(root: Path = ROOT):
    """Usado pela varredura do vault (vault.py): imprime o check sem derrubar o fluxo."""
    cmd_check(load(root), date.today(), root=root)


def main(args) -> int:
    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0 if args else 2
    tasks = load()
    cmd, rest = args[0], args[1:]
    today = date.today()
    if cmd == "foco":
        return cmd_foco(tasks, today)
    if cmd == "lista":
        return cmd_lista(tasks, rest)
    if cmd == "check":
        return cmd_check(tasks, today, everything="--tudo" in rest)
    print(f"subcomando desconhecido: {cmd} (foco, lista, check)", file=sys.stderr)
    return 2
