# Review Checklist

## Git Safety

- Run `git status --short` before reviewing.
- Separate unrelated local changes from the review target.
- Never run `git reset --hard`, `git checkout --`, destructive cleanup, or production-impacting commands without explicit user approval.

## Findings First

- Put bugs and regressions before summary.
- Order by severity.
- Use file/line references.
- Explain impact and a concrete fix direction.

## Migrations And Data Cleanup

- Identify irreversible deletes, drops, truncates, and backfills.
- Check rollback or abort strategy.
- Check idempotency, batching, locks, and timeouts.
- Require fixture tests for data transformations.
- Ask for environment boundaries before any production-touching operation.
