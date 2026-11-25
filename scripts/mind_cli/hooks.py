"""Hooks do Claude Code, em Python (sem shell, igual em qualquer sistema).

Uso (no settings.json, forma `args`): python scripts/mind.py hook session-start
Junta todos os avisos do início de sessão num único JSON de `additionalContext`.
"""
import json
import re
import sys
from datetime import date, datetime

from .common import ROOT, read_text
from .platform_ import claude_home

PY = "python scripts/mind.py"


def check_config():
    cfg = ROOT / "config.md"
    if cfg.is_file() and "**Resposta:** (ainda não respondido)" in read_text(cfg):
        return ("O arquivo config.md do Mind tem perguntas de configuração inicial sem resposta. Leia "
                "config.md, identifique quais perguntas estão marcadas como (ainda não respondido), "
                "pergunte ao usuário logo no início desta conversa (pode agrupar via AskUserQuestion), "
                "e grave as respostas no arquivo.")


def check_manutencao():
    f = ROOT / "docs" / "MANUTENCAO.md"
    if not f.is_file():
        return None
    dates = re.findall(r"^- (\d{4}-\d{2}-\d{2})", read_text(f), re.M)
    if not dates:
        return None
    days = (date.today() - datetime.strptime(dates[-1], "%Y-%m-%d").date()).days
    if days < 7:
        return None
    return (f"A última rodada de manutenção do Mind (docs/MANUTENCAO.md) foi há {days} dias (>= 7). "
            "Pergunte ao usuário logo no início desta conversa se ele quer rodar uma nova rodada de "
            "manutenção do vault agora (dedup/compactação de histórico + reconciliação com vault "
            f"complementar + propagação de convenções novas + checagem de versão do template via {PY} "
            "template; critérios e mecanismo em docs/ARQUITETURA.md, seção 11). Só prossiga se ele "
            "confirmar explicitamente — e quando confirmar, delegue o trabalho pesado pro subagente "
            "maintenance (Agent tool, subagent_type maintenance) em vez de ler tudo direto nesta "
            "conversa; só relaie o resumo que ele devolver. Persona: leia a resposta de Mineração de "
            "conversas antigas no config.md — se for perguntar (e a persona não estiver desligada), "
            "inclua na mesma pergunta se ele quer minerar também; se for automático, minere sem "
            "perguntar; em ambos, avise o subagente no prompt que a mineração foi aprovada. Ao receber "
            "o resumo, se vierem Amostras candidatas, pergunte ao usuário quais manter e só então "
            "grave em persona.md.")


def check_symlink():
    if not (claude_home() / "mind-vault").exists():
        return (f"O link ~/.claude/mind-vault (usado pela persona espelho) ainda não existe nesta "
                f"máquina. Avise o usuário logo no início desta conversa que precisa rodar "
                f"`{PY} setup` (e ofereça rodar por ele); sem isso a persona espelho não carrega "
                "em outros projetos.")


def session_start() -> int:
    msgs = [m for m in (check_config(), check_manutencao(), check_symlink()) if m]
    if msgs:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n\n".join(msgs)}}))
    return 0


def main(args) -> int:
    if args[:1] == ["session-start"]:
        return session_start()
    print("uso: mind.py hook session-start", file=sys.stderr)
    return 2
