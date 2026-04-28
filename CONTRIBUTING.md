# Contributing

Contributions should improve the skill's ability to help agents safely share experience, optimize skills, publish services, and participate in EvoMap credit workflows.

Before opening a PR:

1. Do not include secrets, real `node_secret` values, private tokens, or account screenshots.
2. Keep `SKILL.md` concise. Put long explanations in `references/`.
3. Prefer safety defaults: no automatic credit spend, no hidden full fetch, no automatic public publish.
4. Run:
   ```bash
   python3 scripts/validate.py
   ```
5. Explain which agent platform you tested: Codex, Claude Code, Cursor, or another agent.
