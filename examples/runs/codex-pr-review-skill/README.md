# Demo Run: Codex PR Review Skill Evolution

Generated at: 2026-04-28T07:42:23.983575+00:00

## Core Scenario

A user has a simple Codex review skill. It fails on a database cleanup migration review because it summarizes first, misses git preflight, and does not guard destructive data changes. EvoMap-style metadata search contributes reusable patterns without spending credits. The skill evolves, validates, and is packaged for EvoMap Skill Store publishing.

## Steps

1. Seed local skill: `initial/codex-pr-reviewer/SKILL.md`
2. Capture task feedback: `evidence/task-feedback.json`
3. Search metadata only: `evomap/search-only-candidates.json` (0 credits)
4. Evolve skill: `evolved/codex-pr-reviewer/SKILL.md`
5. Validate: `validation/validation-report.json` (8/8 checks, score 100)
6. Prepare publish dry-run package: `publish/skill-store-publish-payload.json`
7. Prepare Gene/Capsule preview: `publish/gene-capsule-preview.json`
8. Prepare service listing: `publish/service-listing-draft.json`

## Credit Story

- Search-only metadata spend: 0 credits.
- Full fetches: 0.
- Live publish: not attempted; dry-run package generated.
- Monetization path: publish skill for distribution, sell the service for repeated skill evolution work, and earn credits through bounties or asset reuse when accepted by EvoMap quality gates.

## Human Confirmation Gates

- Publish to Skill Store requires real `EVOMAP_NODE_ID` / `EVOMAP_NODE_SECRET` and explicit `--publish-live`.
- Public visibility, paid full fetch, bounty claim, and service publication remain manual decisions.
