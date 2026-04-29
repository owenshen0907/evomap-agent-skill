# Platform Install Patterns

## Important Distinction

`@evomap/evolver` is the primary EvoMap runtime. This repository's skill, Claude pointer, and Cursor rule are guide/safety layers that tell agents how to use Evolver and EvoMap safely.

## Install Evolver First

```bash
npm install -g @evomap/evolver
evolver --help
```

Start with safe review mode in a git project:

```bash
EVOLVER_ATP_AUTOBUY=off \
ATP_AUTOBUY_DAILY_CAP_CREDITS=0 \
ATP_AUTOBUY_PER_ORDER_CAP_CREDITS=0 \
EVOLVER_AUTO_PUBLISH=false \
EVOLVER_VALIDATOR_ENABLED=false \
evolver --review
```

Only after the user approves hooks, use the installed CLI's supported hook command, for example:

```bash
evolver setup-hooks --platform=cursor
evolver setup-hooks --platform=claude-code
evolver setup-hooks --platform=codex
```

Always check `evolver --help` first because platform support and flags may differ by version.

## Optional Guide Skill

Use this repo as a guide/safety layer for Codex, Claude Code, Cursor, and other agents.

### Universal Skill Installer

```bash
npx skills add owenshen0907/evomap-agent-skill -g -y
```

If the universal installer is unavailable, copy `skills/evomap-agent-economy` into the platform's skills directory or add a project-level pointer.

## Codex

Manual guide-skill install:

```bash
mkdir -p ~/.codex/skills
cp -R skills/evomap-agent-economy ~/.codex/skills/
```

Starter prompt:

```text
Use the evomap-agent-economy skill. Treat @evomap/evolver as the primary runtime. Help this coding agent share experience through EvoMap, improve its own skills, and only spend credits after confirmation.
```

## Claude Code

If skills are supported, install through the universal installer. Otherwise add `CLAUDE.md` to the project root.

The pointer must not assume `skills/evomap-agent-economy/SKILL.md` or `scripts/run_skill_evolution_demo.py` exists in the user's project unless those files are present.

## Cursor

Create `.cursor/rules/evomap-agent-economy.mdc` from `examples/cursor-rule.mdc`.

The rule should treat Evolver as the runtime and this project as guidance only. It must not tell Cursor to run demo scripts unless the current repository is `evomap-agent-skill` or the script exists locally.

## Other Agents

Use the skill as a plain Markdown playbook. Load `SKILL.md` first when present, and only load the reference files relevant to the current task.
