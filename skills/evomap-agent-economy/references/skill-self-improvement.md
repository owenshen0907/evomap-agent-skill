# Skill Self-Improvement Loop

Use this loop to help an agent improve its own skills without unsafe self-modification.

## Evidence Sources

- Repeated user corrections.
- Failed commands or tests.
- Successful workflows that required many manual steps.
- Repeated troubleshooting patterns.
- Bounty task outcomes.
- Service delivery feedback.
- Asset fetch results and rejection reasons.

## Patch Types

| Patch type | When to use |
|---|---|
| Trigger metadata | The skill should activate in more/less specific situations |
| Workflow step | A missing step caused errors or repeated questions |
| Guardrail | A risky action needs confirmation or a safer default |
| Reference file | Details are too long for `SKILL.md` |
| Script | A repeated operation needs deterministic validation |
| Example | Agents keep misunderstanding the expected output |

## Procedure

1. State the observed failure or opportunity.
2. Locate the skill file and relevant references.
3. Make the smallest patch that changes future behavior.
4. Keep `SKILL.md` concise; move details to `references/`.
5. Validate frontmatter and required files.
6. Dry-run with a realistic prompt.
7. Summarize the changed behavior.

## Publishing As Experience

If the improvement is generally useful:

1. Convert it into a clean Skill, Gene/Capsule bundle, or service playbook.
2. Remove private details and credentials.
3. Add validation commands or proof of usefulness.
4. Publish only after human review.

## Do Not

- Rewrite a global skill in place without a backup or diff.
- Encode private user preferences into a public skill.
- Publish raw logs containing secrets.
- Claim broad capability without evidence.
