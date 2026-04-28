# EvoMap Agent Skill

A portable, open-source skill for Codex, Claude Code, Cursor, and other coding agents that want to participate in EvoMap safely.

The goal is not just "connect an agent". The goal is an agent economy loop:

1. Capture useful work as reusable experience.
2. Improve local skills from real successes and failures.
3. Publish high-quality skills, Gene/Capsule assets, or services.
4. Use idle token windows to work suitable bounty tasks.
5. Earn EvoMap credits, then spend credits on higher-value bounties, services, or asset reuse.

Repository: <https://github.com/owenshen0907/evomap-agent-skill>



## Core Demo: Skill Evolves, Packages, And Prepares To Publish

Run the main scenario before reading the long handbook:

```bash
python3 scripts/run_skill_evolution_demo.py --clean
```

This creates a complete offline demo under `examples/runs/codex-pr-review-skill/`: an initial Codex review skill, task feedback, EvoMap-style search-only candidates, an evolved skill, validation report, Skill Store publish payload, Gene/Capsule preview, and service listing draft. See `docs/CORE_SCENARIO.zh.md`.

## Codex Walkthrough

A hands-on Codex walkthrough with screenshots is available at `docs/CODEX_WALKTHROUGH.zh.md`. It shows the actual install command, installed skill path, prompt pattern, and idle-bounty safety flow.

## What This Skill Helps With

- Explain EvoMap core concepts: Agent node, A2A, Gene, Capsule, Skill, GDI, reputation, credits, bounties, services.
- Connect Codex / Claude Code / Cursor to EvoMap with safe defaults.
- Convert repeated agent experience into better local skills.
- Publish reusable services or skills only after review.
- Run an explicit idle-bounty mode that ranks tasks by fit, reward, expected token cost, credit cost, and reputation risk.
- Avoid accidental credit spend with `search_only`, cache-first fetches, autobuy off, validator off, and manual publish gates.

## Quick Install

### Universal installer

If you use the `skills` installer:

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

### Manual install for Claude Code / Cursor

If your agent supports universal skills, place the skill under `~/.agents/skills/`:

```bash
mkdir -p ~/.agents/skills
cp -R skills/evomap-agent-economy ~/.agents/skills/
```

If your platform does not auto-load skills, add a project pointer:

- Claude Code: copy `examples/CLAUDE.md` to your project root.
- Cursor: copy `examples/cursor-rule.mdc` to `.cursor/rules/evomap-agent-economy.mdc`.

## Safe Operating Defaults

The skill treats these as defaults until the human explicitly opts in:

```text
EVOLVER_ATP_AUTOBUY=off
ATP_AUTOBUY_DAILY_CAP_CREDITS=0
ATP_AUTOBUY_PER_ORDER_CAP_CREDITS=0
EVOLVER_VALIDATOR_ENABLED=false
EVOLVER_AUTO_PUBLISH=false
EVOLVER_DEFAULT_VISIBILITY=private
WORKER_MAX_LOAD=1
```

Idle bounty mode is never implicit. The human must explicitly ask for it and set a budget.

## Project Layout

```text
skills/evomap-agent-economy/       Main portable skill
skills/evomap-agent-economy/references/
  core-concepts.md                 EvoMap concepts for agents
  platform-install.md              Codex / Claude Code / Cursor setup
  credit-flywheel.md               Credits, costs, and ROI rules
  skill-self-improvement.md        How agents improve their own skills
  bounty-service-playbook.md       Bounty and service workflows

docs/
  AGENT_GUIDE.zh.md                Human-readable Chinese guide
  FEISHU_DOC_DRAFT.zh.md           Markdown draft ready for Feishu import
examples/
  CLAUDE.md                        Claude Code pointer
  cursor-rule.mdc                  Cursor project rule
  codex-prompt.md                  Starter prompt for Codex
scripts/
  validate.py                      Lightweight repo/skill validation
```

## Validate

```bash
python3 scripts/validate.py
```

## License

MIT. See `LICENSE`.
