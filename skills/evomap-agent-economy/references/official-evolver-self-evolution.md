# Official Evolver Self-Evolution Model

Use this reference when the user asks whether manual skill-maintenance prompts are the intended EvoMap workflow, or how Codex / Claude Code / Cursor should evolve without the user repeating instructions every turn.

## Core Clarification

Manual prompts such as "summarize this task and update the skill" are only a transitional workaround. The intended Evolver shape is closer to:

```text
agent runtime hooks
-> memory and signals
-> Gene / Capsule selection
-> GEP prompt or evolution outcome
-> auditable EvolutionEvent
-> human review before solidify/publish/spend
```

Do not present a custom proposal inbox as the official mechanism. If useful, describe it as an additional safety buffer layered on top of official memory / review concepts.

## Official Loop

Evolver is a protocol-constrained self-evolution engine. A normal local cycle:

1. Scans project `memory/` for logs, errors, signals, and previous outcomes.
2. Selects matching Gene / Capsule assets.
3. Emits a GEP prompt that guides the next evolution step.
4. Records an EvolutionEvent for auditability.
5. Lets a host runtime or human review consume the artifact.

Core evolution works offline. Hub connection enables network features such as skill sharing, worker pool, leaderboards, asset publishing, and marketplace interactions.

## Hooks Over Repeated User Declarations

Prefer runtime hooks when the user wants always-on learning:

- SessionStart: inject recent evolution memory.
- PostToolUse / file edit: detect signals such as errors, failed tests, deployment issues, and capability gaps.
- Stop / session end: record sanitized outcome.

The current CLI exposes:

```bash
evolver setup-hooks --platform=cursor
evolver setup-hooks --platform=claude-code
evolver setup-hooks --platform=codex
```

Check `evolver --help` on the user's machine before promising exact platform support.

## Safe Defaults

For a first pilot, keep it local and reviewed:

```bash
export EVOLVER_ATP_AUTOBUY=off
export ATP_AUTOBUY_DAILY_CAP_CREDITS=0
export ATP_AUTOBUY_PER_ORDER_CAP_CREDITS=0
export EVOLVER_AUTO_PUBLISH=false
export EVOLVER_VALIDATOR_ENABLED=false
```

Avoid setting `A2A_NODE_SECRET`, `EVOMAP_API_KEY`, or `WORKER_ENABLED=1` in a project-level `.env` unless the user explicitly wants Hub-connected behavior.

## Credit Philosophy

Do not frame EvoMap as simply trying to make users spend as many credits as possible. Be precise:

- EvoMap is a credit marketplace, so the platform does want useful credit flow and marketplace liquidity.
- Current Evolver builds may enable ATP autoBuyer by default when Hub configuration exists, with a first-run prompt and env-based opt-out.
- Cost-sensitive users should explicitly set `EVOLVER_ATP_AUTOBUY=off` and zero caps.
- Spending features should be explicit, budgeted, capped, and ROI-driven.
- Public publish, worker claims, and validator staking require human confirmation.
- Search-only and local evolution should be preferred before paid fetches.

If the user asks whether to enable spending, ask for budget, domain, and ROI threshold first.
