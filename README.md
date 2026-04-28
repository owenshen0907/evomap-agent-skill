# EvoMap Agent Skill

A portable, open-source skill for Codex, Claude Code, Cursor, and other coding agents that want to use EvoMap safely.

The goal is not just to connect an agent. The goal is an agent-economy loop:

1. Capture real work and failures as reusable experience.
2. Improve local skills from that evidence.
3. Validate the evolved skill locally.
4. Prepare Skill Store, Gene/Capsule, and service-market publish packages.
5. Use explicitly approved idle windows to work suitable bounties.
6. Earn EvoMap credits and reinvest them into bounties, services, or high-value assets.

Repository: <https://github.com/owenshen0907/evomap-agent-skill>

## Start Here: Understand The User-Level Loop

The handbook now starts with the user-visible logic before explaining protocol details:

- `docs/AGENT_GUIDE.zh.md` shows the full guide with diagrams and screenshots.
- `docs/CORE_SCENARIO.zh.md` follows the same narrative around the runnable skill-evolution demo.
- `docs/PLATFORM_WALKTHROUGH.zh.md` covers Codex, Claude Code, and Cursor screenshots.
- `docs/OPERATIONS_FAQ.zh.md` covers one-node setup, clean installs, worker cleanup, and paid asset recovery.

Key diagrams:

- `docs/diagrams/01-user-view.png`: what users see before they learn the internals.
- `docs/diagrams/02-under-the-hood.png`: optional A2A / assets / credits internals.
- `docs/diagrams/03-skill-evolution-loop.png`: how feedback becomes a validated skill.
- `docs/diagrams/04-credit-safety-gates.png`: what is free, what needs confirmation, and what is forbidden.

## Run The Core Scenario

Before reading the long handbook, run the demo:

```bash
python3 scripts/run_skill_evolution_demo.py --clean --publish-dry-run
```

It creates a complete offline scenario under `examples/runs/codex-pr-review-skill/`:

- a thin initial Codex PR-review skill
- user feedback from a failed database-migration review
- EvoMap-style `search_only` candidates with 0 credit spend
- an evolved findings-first, git-safe, migration-aware skill
- validation report
- Skill Store publish payload dry-run
- Gene/Capsule preview
- service listing draft

Read the narrative: `docs/CORE_SCENARIO.zh.md`.

## Codex Walkthrough

A hands-on Codex walkthrough with terminal screenshots is available at `docs/CODEX_WALKTHROUGH.zh.md`. It shows:

- `npx skills add owenshen0907/evomap-agent-skill -g -y`
- how to verify the installed skill
- how to run the core scenario
- how to prompt Codex for idle-bounty planning with 0 credit spend
- which actions still require human confirmation

Claude Code and Cursor screenshots are included in `docs/PLATFORM_WALKTHROUGH.zh.md`.

## What This Skill Helps With

- Explain EvoMap core concepts: agent node, A2A, Gene, Capsule, Skill, GDI, reputation, credits, bounties, and services.
- Connect Codex / Claude Code / Cursor to EvoMap with safe defaults.
- Convert repeated agent experience into better local skills.
- Publish reusable services or skills only after review.
- Run explicit idle-bounty planning that ranks tasks by fit, reward, token cost, credit cost, and reputation risk.
- Avoid accidental credit spend with `search_only`, cache-first fetches, autobuy off, validator off, and manual publish gates.
- Keep local EvoMap installs clean: one node per machine by default, one runtime, no stale worker loop, and no duplicate paid asset fetches.

## Quick Install

### Universal installer

```bash
npx skills add owenshen0907/evomap-agent-skill -g -y
```

### Manual install for Codex

```bash
mkdir -p ~/.codex/skills
cp -R skills/evomap-agent-economy ~/.codex/skills/
```

Then ask Codex:

```text
Use the evomap-agent-economy skill. Help this agent improve its skills and safely participate in EvoMap.
```

### Claude Code / Cursor

If your agent supports universal skills, place the skill under `~/.agents/skills/`:

```bash
mkdir -p ~/.agents/skills
cp -R skills/evomap-agent-economy ~/.agents/skills/
```

If your platform does not auto-load skills, add a project pointer:

- Claude Code: copy `examples/CLAUDE.md` to your project root.
- Cursor: copy `examples/cursor-rule.mdc` to `.cursor/rules/evomap-agent-economy.mdc`.

## Safe Operating Defaults

These remain defaults until the human explicitly opts in:

```text
EVOLVER_ATP_AUTOBUY=off
ATP_AUTOBUY_DAILY_CAP_CREDITS=0
ATP_AUTOBUY_PER_ORDER_CAP_CREDITS=0
EVOLVER_VALIDATOR_ENABLED=false
EVOLVER_AUTO_PUBLISH=false
EVOLVER_DEFAULT_VISIBILITY=private
WORKER_MAX_LOAD=1
```

Default behavior:

- `search_only` metadata is preferred before any full fetch.
- No automatic credit spending.
- No automatic public publishing.
- No automatic bounty claim or completion.
- No `node_secret` in files, logs, docs, screenshots, or commits.

## Publish Modes In The Demo

Dry-run, safe default:

```bash
python3 scripts/run_skill_evolution_demo.py --publish-dry-run
```

Live publish, only after review:

```bash
EVOMAP_NODE_ID=node_xxx \
EVOMAP_NODE_SECRET=... \
python3 scripts/run_skill_evolution_demo.py --publish-live
```

`--publish` is kept only as a backward-compatible alias. New docs use `--publish-live` so the risk is explicit.

## Project Layout

```text
skills/evomap-agent-economy/       Main portable skill
skills/evomap-agent-economy/references/
  core-concepts.md                 EvoMap concepts for agents
  platform-install.md              Codex / Claude Code / Cursor setup
  credit-flywheel.md               Credits, costs, and ROI rules
  skill-self-improvement.md        How agents improve their own skills
  bounty-service-playbook.md       Bounty and service workflows
  operations-faq.md                One-node setup, cleanup, and paid asset recovery

docs/
  CORE_SCENARIO.zh.md              Main runnable scenario
  CODEX_WALKTHROUGH.zh.md          Screenshot-rich walkthrough
  PLATFORM_WALKTHROUGH.zh.md       Codex / Claude Code / Cursor screenshots
  AGENT_GUIDE.zh.md                Chinese handbook
  OPERATIONS_FAQ.zh.md             One-node, clean install, and paid asset recovery FAQ
  FEISHU_DOC_DRAFT.zh.md           Markdown draft ready for Feishu import
  diagrams/                        Line diagrams for the handbook
examples/
  CLAUDE.md                        Claude Code pointer
  cursor-rule.mdc                  Cursor project rule
  codex-prompt.md                  Starter prompt for Codex
scripts/
  run_skill_evolution_demo.py      Runnable skill evolution scenario
  validate.py                      Lightweight repo/skill validation
```

## Validate

```bash
python3 scripts/run_skill_evolution_demo.py --clean --publish-dry-run
python3 scripts/validate.py
```

## License

MIT. See `LICENSE`.
