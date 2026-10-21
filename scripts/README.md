---
tags: [engine, scripts]
criado: 2026-10-20
atualizado: 2026-10-20
---

# Scripts do Mind

Utilitários locais, rodados sob demanda (nenhum é daemon). Voltar ao [índice](../MIND.md).

- [status-all.sh](status-all.sh) — varre os repos git do array `REPOS` e mostra quais têm mudança não commitada ou commit não enviado.
- [buscar.sh](buscar.sh) — busca um termo no vault inteiro (conteúdo e nome de arquivo, sem acento nem maiúscula) e devolve só os arquivos que mais citam, com uma linha de contexto; usar antes de dizer que o Mind não tem uma informação.
- [check-orfaos.sh](check-orfaos.sh) — lista os arquivos do vault que nenhum `.md` linka (nós soltos no grafo do MindView); roda na [manutenção](../docs/ARQUITETURA.md).
- [check-template-version.sh](check-template-version.sh) — avisa se o engine deste vault está atrás do `mind-template` (só leitura).
- [setup-symlinks.sh](setup-symlinks.sh) — recria os symlinks de `claude-user/` em `~/.claude/` depois de um `git clone`.
- [extract-user-messages.sh](extract-user-messages.sh) — extrai dos transcripts locais só as mensagens do usuário, matéria-prima da mineração da persona.
