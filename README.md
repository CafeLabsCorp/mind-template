[Leia em Português](README.pt-br.md)

# Mind — template

A personal knowledge base organized as a tree of Markdown files, meant to be edited visually in an [Obsidian](https://obsidian.md)-like editor and queried on demand by **[Claude Code](https://claude.com/claude-code)** — Anthropic's official CLI. This repository only really works alongside it: it's `claude` running in your terminal that reads the Skill and the capture trigger here, and decides when to look something up or save it. Without Claude Code installed, the vault is just a plain folder of Markdown.

This repository is the **raw/template version**: only the engineering (Skill, capture trigger, symlink script, architecture docs), with no personal content. Clone it, personalize it, and start filling it with your own nodes.

The full architecture (why each decision was made, what's still missing) is in [docs/ARQUITETURA.md](docs/ARQUITETURA.md). This README is just the "how to use it".

## Prerequisites

- **[Claude Code](https://claude.com/claude-code) installed** and configured (`claude` available in your terminal) — see the official install guide at the link.
- Optional: a Markdown editor with graph/backlink support, like [Obsidian](https://obsidian.md), to navigate and edit nodes visually. Not required — you can use it from the terminal alone.

## What's in here

- **`MIND.md`**: root index, starts empty. There's no fixed pre-built folder tree — nodes (and whatever folders make sense to organize them) get created gradually, as conversations happen.
- **`.claude/`**: Skill and permissions that only apply while this project is active.
- **`claude-user/`**: the "warehouse" for **user-level** Skill, Subagents, and instructions — they work in any active project, not just this one. They live here (versioned in this repo) and get mirrored into `~/.claude/` via symlink (see below).
- **`scripts/setup-symlinks.sh`**: recreates the `claude-user/` symlinks in `~/.claude/`.
- **`scripts/status-all.sh`**: scans whatever project repos you list inside it and shows which ones have uncommitted changes or unpushed commits — to check everything at once instead of going folder by folder.
- **`scripts/check-template-version.sh`**: reports whether your engineering base is behind this template (read-only).
- **`VERSION` / `CHANGELOG.md`**: version number of the engineering base and what changed in each bump — used by the check above and by the maintenance round.

## Setup on a new machine

Clone it as a "manual" fork via git (two remotes) — that way you can pull future updates
from the template (section below) without losing your own nodes. **Don't** use GitHub's
"Use this template" button: it creates a git history disconnected from the original and
breaks this flow (full reasoning in [docs/ARQUITETURA.md](docs/ARQUITETURA.md), section 12).

1. Create an **empty, private** repository (GitHub, GitLab, etc.) to hold your vault —
   don't initialize it with a README/license/gitignore, it needs to be truly empty.
2. Clone the template and re-point it to that empty repo — use SSH if you already have a
   key configured on GitHub (won't ask for a password afterward), or HTTPS if you don't
   (always works, but asks for username/token on every push). You can mix protocols:
   `upstream` on one and `origin` on the other, no problem.

   **Via SSH:**

   ```bash
   git clone git@github.com:CafeLabsCorp/mind-template.git mind
   cd mind
   git remote rename origin upstream
   git remote add origin <ssh-url-of-your-empty-repo>
   git push -u origin main
   ```

   **Via HTTPS:**

   ```bash
   git clone https://github.com/CafeLabsCorp/mind-template.git mind
   cd mind
   git remote rename origin upstream
   git remote add origin <https-url-of-your-empty-repo>
   git push -u origin main
   ```

3. Run the setup and start using it:

   ```bash
   ./scripts/setup-symlinks.sh
   claude
   ```

You can clone it under any name and at any path — there's no fixed-location requirement, unless you're using a voice integration (see section below).

Running `./scripts/setup-symlinks.sh` again is safe at any time (idempotent) — only needed when a new Skill/Subagent gets added under `claude-user/`.

From there it's just conversation: ask it to look something up, or mention something worth keeping — the Skill and the trigger handle the rest (see section below).

## Receiving template updates

This repository evolves (new Skill rules, architecture tweaks). Since the setup above already configured `upstream`, pulling updates later is always:

```bash
git fetch upstream
git merge upstream/main
```

This usually merges without conflict because the architecture already separates "engineering" (`docs/`, `claude-user/`, `scripts/`, `.claude/`) — which only changes here, in the template — from personal content (your filled-in `MIND.md` and whatever node folders you create) — which the template never touches. The expected friction point is `.claude/settings.json`: it accumulates permissions granted as you use it, so if you and the template change that file at the same time you can get a merge conflict there — rare, and resolves by hand without mystery (small file). More details on this decision in [docs/ARQUITETURA.md](docs/ARQUITETURA.md), section 12.

**Knowing when you're behind:** the engineering base has a version number in [`VERSION`](VERSION), and each bump is described in [`CHANGELOG.md`](CHANGELOG.md). The periodic maintenance round (section below) runs `scripts/check-template-version.sh`, which compares your local `VERSION` against the template's and tells you if you're behind — it only reports; the `git merge` above stays your call. The check needs no local copy of the template: it uses a sibling `../mind-template` if you keep one, otherwise `git fetch upstream`.

## How knowledge capture works

During any conversation with Claude Code, in any project, if something looks like a fact/decision/personal preference worth keeping, Claude asks before saving it. If confirmed, it edits the right node itself (or creates a new one) and updates the index in `MIND.md`. The full logic lives in `claude-user/CLAUDE.md` (trigger) and `claude-user/skills/mind/SKILL.md` (procedure).

Nothing is saved without confirmation — and nothing stops you from editing files by hand at any time; Claude only reads the current state of the files when queried.

## Voice integration (optional)

You can plug in an external voice assistant that resolves the "active project" by voice and runs Claude Code pointed at it. This is entirely optional — without it, Mind works normally with Claude Code on the keyboard alone. Details of the general pattern are in `docs/ARQUITETURA.md`, section 8.

## Development agent team (optional)

Mind organizes personal knowledge — it doesn't include a team of agents for building software. If you also build products/MVPs and want an orchestrator + specialists pattern to speed that up, [Café Labs Forge](https://github.com/CafeLabsCorp/forge) is a ready-made, fully decoupled complement (its own repository, doesn't depend on Mind or vice versa). Details in `docs/ARQUITETURA.md`, section 9.

## Make it private once it's filled in

As soon as you start adding knowledge nodes with personal information, keep the repository private. All of this template's "engineering" (Skill, symlink script, structure, this README, `docs/ARQUITETURA.md`) is generic and can stay public/shareable — only the content you create needs to stay private.
