"""Avisa se o engine deste vault está atrás do mind-template. Só leitura: nunca mescla nem edita.

Acha a versão do template sem precisar de clone local:
  1. uma pasta irmã ../mind-template/VERSION, se existir
  2. o remote 'upstream' (git fetch upstream; lê VERSION de upstream/main)
  3. senão: pula, com a dica de como habilitar
"""
import re
from pathlib import Path

from .common import ROOT
from .platform_ import run


def digits(s: str) -> int:
    d = re.sub(r"\D", "", s or "")
    return int(d) if d else 0


def read_version(path: Path) -> int:
    try:
        return digits(path.read_text(encoding="utf-8"))
    except OSError:
        return 0


def main(args) -> int:
    local = read_version(ROOT / "VERSION")
    remote, source = 0, ""

    sibling = ROOT.parent / "mind-template" / "VERSION"
    if sibling.is_file():
        remote = read_version(sibling)
        if remote:
            source = "../mind-template (clone local)"

    if not remote:
        url = run(["git", "-C", str(ROOT), "remote", "get-url", "upstream"])
        if url.returncode == 0:
            if run(["git", "-C", str(ROOT), "fetch", "upstream", "--quiet"]).returncode == 0:
                shown = run(["git", "-C", str(ROOT), "show", "upstream/main:VERSION"])
                remote = digits(shown.stdout)
                if remote:
                    source = f"remote 'upstream' ({url.stdout.strip()})"

    if not remote:
        print("TEMPLATE_CHECK: skipped — template não encontrado (nem ../mind-template, nem remote 'upstream').")
        print("  Para habilitar: git remote add upstream https://github.com/CafeLabsCorp/mind-template.git")
        return 0

    if local >= remote:
        print(f"TEMPLATE_CHECK: em dia — engine local v{local}, template v{remote} (via {source}).")
    else:
        print(f"TEMPLATE_CHECK: ATRÁS — engine local v{local}, template v{remote} (via {source}).")
        print(f"  Veja o CHANGELOG.md do template para o que mudou entre v{local} e v{remote}.")
        print("  Aplicar: 'git fetch upstream && git merge upstream/main' (fluxo de dois remotes), ou à mão.")
    return 0
