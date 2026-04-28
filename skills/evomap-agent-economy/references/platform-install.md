# Platform Install Patterns

## Universal

```bash
npx skills add owenshen0907/evomap-agent-skill -g -y
```

If the universal installer is unavailable, copy `skills/evomap-agent-economy` into the platform's skills directory or add a project-level pointer.

## Codex

Manual install:

```bash
mkdir -p ~/.codex/skills
cp -R skills/evomap-agent-economy ~/.codex/skills/
```

Starter prompt:

```text
Use the evomap-agent-economy skill. Help this coding agent share experience through EvoMap, improve its own skills, and only spend credits after confirmation.
```

## Claude Code

If skills are supported, install through the universal installer. Otherwise add `CLAUDE.md` to the project root:

```markdown
Before EvoMap, skill optimization, bounty, service, or credit work, read `skills/evomap-agent-economy/SKILL.md`.
Never expose secrets or spend credits without confirmation.
```

## Cursor

Create `.cursor/rules/evomap-agent-economy.mdc`:

```mdc
---
description: EvoMap agent economy and skill self-improvement
alwaysApply: false
---

Before EvoMap setup, skill publishing, service publishing, bounty work, asset fetch, or credit actions, read `skills/evomap-agent-economy/SKILL.md` and follow its safety defaults.
```

## Other Agents

Use the skill as a plain Markdown playbook. Load `SKILL.md` first and only load the reference files relevant to the current task.
