# Demo Run: Checkout Discount Code Evolution

Generated at: demo run time (timestamp omitted for stable repository diffs)

## Core Scenario

A checkout coupon helper fails real unit tests. Evolver-style review treats the failing tests as evidence, uses search-only metadata at 0 credits, fixes the code, validates the result, and distills the lesson into a reusable local skill plus publish/service drafts.

## Steps

1. Seed buggy code: `initial/checkout_pricing/pricing.py`
2. Reproduce failure: `evidence/initial-test-output.txt`
3. Capture evidence: `evidence/task-feedback.json`
4. Search metadata only: `evomap/search-only-candidates.json`
5. Fix code: `evolved/checkout_pricing/pricing.py`
6. Create local skill: `evolved/skills/payment-edge-case-reviewer/SKILL.md`
7. Validate: `validation/validation-report.json` (8/8 checks, score 100)
8. Prepare Gene/Capsule, Skill Store payload, and service draft under `publish/`

## Credit Story

- Search-only metadata spend: 0 credits.
- Full fetches: 0.
- Live publish: not attempted.
- Monetization path: publish the local skill or Gene/Capsule after review, or sell a service that fixes checkout money bugs and turns the outcome into reusable agent experience.
