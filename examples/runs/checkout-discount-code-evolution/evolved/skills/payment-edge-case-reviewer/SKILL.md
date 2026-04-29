---
name: payment-edge-case-reviewer
description: Review checkout, billing, coupon, tax, refund, and money-calculation code for rounding, bounds, validation, and regression tests. Use when code touches integer cents, percentages, discounts, refunds, invoices, or user-entered monetary inputs.
---

# Payment Edge Case Reviewer

## Goal

Catch production-facing money bugs before they ship. Treat failing tests and user feedback as reusable evidence, not one-off fixes.

## Workflow

1. Run the targeted tests before editing, and save the failure output.
2. Identify the money invariant: non-negative total, bounded percentage, integer cents, explicit rounding, and typed inputs.
3. Patch the smallest function that violates the invariant.
4. Add or keep boundary tests for 0%, 100%, over-100%, negative inputs, and fractional-cent rounding.
5. Re-run the targeted tests and record the passing command.
6. Convert the lesson into a reusable checklist or Gene/Capsule only after validation passes.

## Review Checklist

- Do not use binary floats for money math when rounding behavior matters.
- Use integer cents or Decimal with an explicit rounding mode.
- Reject negative user-entered monetary values unless the domain explicitly allows them.
- Clamp over-100% discounts or reject them according to product policy.
- Prefer tests that describe user-visible failures, not only implementation details.
