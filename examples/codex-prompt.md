Use the `evomap-agent-economy` skill.

First, run the local skill-evolution demo if this repo is available:

```bash
python3 scripts/run_skill_evolution_demo.py --clean --publish-dry-run
```

Then explain the result in this order:

1. What evidence caused the skill to evolve.
2. Which EvoMap-style `search_only` candidates were used at 0 credits.
3. What changed in the evolved skill.
4. What validation passed locally.
5. What Skill Store / Gene / Capsule / service drafts were prepared.
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
