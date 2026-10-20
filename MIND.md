# Mind — índice

> Só links + 1 linha de descrição cada. Não ler os nós daqui — abrir só o(s) relevante(s) pra pergunta feita. Ver `docs/ARQUITETURA.md` pra entender por quê.

_A árvore vai crescendo aos poucos, conforme as conversas (ver sistema de captura em `claude-user/CLAUDE.md` e `claude-user/skills/mind/SKILL.md`). Cada nó novo criado ganha uma linha aqui, com o link e uma descrição de uma linha._

Configuração inicial de funcionamento (idioma, como chamar o usuário, fuso horário, tom, papel/profissão) fica em [config.md](config.md) — não é um nó de conhecimento, é checado automaticamente no início da sessão (hook `SessionStart`). O perfil de como o usuário fala e age (persona espelho, opt-in no `config.md`) fica em `persona.md` — também não é nó de conhecimento e nasce só quando há o primeiro traço.

## Nós

_Nenhum nó ainda — os primeiros surgem conforme você usa o Mind._

## Engine — como o próprio Mind funciona

- [README](README.md) — apresentação do projeto · [Changelog](CHANGELOG.md) — versões do engine.
- [Arquitetura](docs/ARQUITETURA.md) — como o Mind funciona e por quê · [Manutenção](docs/MANUTENCAO.md) — registro das rodadas periódicas.
- [CLAUDE.md global](claude-user/CLAUDE.md) — regras de trabalho e de captura · [Skill `mind`](claude-user/skills/mind/SKILL.md) — como ler e escrever no vault · [Agente `maintenance`](claude-user/agents/maintenance.md) — roda a manutenção periódica.
- [Scripts](scripts/README.md) — utilitários locais.
