Use the `evomap-agent-economy` skill.

First, treat `@evomap/evolver` as the primary EvoMap runtime. Verify the local CLI before promising exact flags:

```bash
evolver --help
```

If Evolver is not installed, ask before installing it globally:

```bash
npm install -g @evomap/evolver
```

Start in review/safe mode inside a git project:

```bash
EVOLVER_ATP_AUTOBUY=off \
ATP_AUTOBUY_DAILY_CAP_CREDITS=0 \
ATP_AUTOBUY_PER_ORDER_CAP_CREDITS=0 \
EVOLVER_AUTO_PUBLISH=false \
EVOLVER_VALIDATOR_ENABLED=false \
evolver --review
```

Only run the local skill-evolution demo when this repository is available or the script exists:

```bash
python3 scripts/run_skill_evolution_demo.py --clean --publish-dry-run
```

Then explain the result in this order:

1. What evidence caused the skill or workflow to evolve.
2. Whether Evolver used local memory / review output / EvoMap-style `search_only` metadata.
3. What changed in the evolved skill or workflow.
4. What validation passed locally.
5. What Skill Store / Gene / Capsule / service drafts were prepared, if any.
6. Which actions still require human confirmation.

If I explicitly allow idle bounty planning, use this budget:

```text
time_budget_minutes: 60
max_credit_spend: 0
allowed_domains: software_engineering
blocked_domains: credentials, private-key, spam, gambling, adult
publish_visibility: private_or_manual
max_concurrent_tasks: 1
```

Do not spend credits, full-fetch paid assets, claim bounties, publish publicly, or expose `node_secret` without confirmation.
