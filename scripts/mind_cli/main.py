"""Despacha o comando pedido. Cada comando é um módulo com `main(args) -> int`."""
import importlib
import sys

from .common import setup_stdio

COMMANDS = {
    "buscar": ("buscar", "busca um termo no vault inteiro (conteúdo e nome)"),
    "orfaos": ("orfaos", "lista arquivos que nenhum .md linka"),
    "tamanho": ("tamanho", "lista nós .md acima do limite de linhas"),
    "ferramentas": ("ferramentas", "o que está instalado (navegador, node, rclone...) e como instalar o resto"),
    "output": ("output", "pasta de saída (entregas do Claude): caminho, fixar no acesso rápido, listar antigos"),
    "tarefas": ("tarefas", "foco, lista e checagem do board de tarefas (tarefas/)"),
    "vault": ("vault", "varredura completa da manutenção semanal"),
    "template": ("template", "compara a versão do engine com a do mind-template"),
    "status": ("status", "repos com mudança não commitada ou commit não enviado"),
    "drive": ("drive", "espelha binários no Drive (push|pull) via rclone"),
    "setup": ("setup", "cria os links de claude-user/ em ~/.claude/"),
    "mensagens": ("mensagens", "extrai mensagens do usuário dos transcripts (mineração da persona)"),
    "hook": ("hooks", "hooks do Claude Code (ex.: hook session-start)"),
}


def main(argv) -> int:
    setup_stdio()
    if not argv or argv[0] in ("-h", "--help", "help"):
        print("uso: python scripts/mind.py <comando> [argumentos]\n\ncomandos:")
        for name, (_, desc) in COMMANDS.items():
            print(f"  {name:<10} {desc}")
        return 0 if argv else 2
    if argv[0] not in COMMANDS:
        print(f"comando desconhecido: {argv[0]} (veja --help)", file=sys.stderr)
        return 2
    module = importlib.import_module(f"mind_cli.{COMMANDS[argv[0]][0]}")
    return module.main(argv[1:]) or 0
