#!/usr/bin/env python3
"""Run a deterministic code-evolution demo for EvoMap/Evolver docs.

This demo shows the practical "code path" behind the handbook:
1. A small codebase has a real bug and failing tests.
2. The failure becomes evidence for Evolver-style review.
3. Search-only metadata suggests reusable patterns at 0 credits.
4. The code is fixed, tests pass, and the lesson becomes a local skill.
5. Publish/service drafts are prepared, but no live publish happens.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "examples" / "runs" / "checkout-discount-code-evolution"

INITIAL_PRICING = '''"""Checkout pricing helpers.

Amounts are integer cents. Coupon percent is a user-entered integer.
"""


def price_after_coupon_cents(subtotal_cents: int, coupon_percent: int) -> int:
    """Return subtotal after a percentage coupon.

    BUG: this version truncates fractional cents, allows negative coupon
    values, and can return a negative total when coupon_percent > 100.
    """
    discount = int(subtotal_cents * coupon_percent / 100)
    return subtotal_cents - discount
'''

FIXED_PRICING = '''"""Checkout pricing helpers.

Amounts are integer cents. Coupon percent is a user-entered integer.
"""

from decimal import Decimal, ROUND_HALF_UP


def price_after_coupon_cents(subtotal_cents: int, coupon_percent: int) -> int:
    """Return subtotal after a percentage coupon.

    The function validates unsafe inputs, clamps over-100% coupons to a free
    order, and rounds the discount to the nearest cent with half-up semantics.
    """
    if not isinstance(subtotal_cents, int) or not isinstance(coupon_percent, int):
        raise TypeError("subtotal_cents and coupon_percent must be integers")
    if subtotal_cents < 0:
        raise ValueError("subtotal_cents cannot be negative")
    if coupon_percent < 0:
        raise ValueError("coupon_percent cannot be negative")

    bounded_percent = min(coupon_percent, 100)
    discount = (
        Decimal(subtotal_cents) * Decimal(bounded_percent) / Decimal(100)
    ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return max(0, subtotal_cents - int(discount))
'''

TEST_PRICING = '''import unittest

from pricing import price_after_coupon_cents


class PriceAfterCouponTests(unittest.TestCase):
    def test_rounds_half_up_to_nearest_cent(self):
        # 15% of 333 cents is 49.95, so the discount should be 50 cents.
        self.assertEqual(price_after_coupon_cents(333, 15), 283)

    def test_coupon_over_100_percent_cannot_create_negative_total(self):
        self.assertEqual(price_after_coupon_cents(999, 125), 0)

    def test_negative_coupon_is_rejected(self):
        with self.assertRaises(ValueError):
            price_after_coupon_cents(999, -10)

    def test_negative_subtotal_is_rejected(self):
        with self.assertRaises(ValueError):
            price_after_coupon_cents(-1, 10)

    def test_full_discount_is_zero(self):
        self.assertEqual(price_after_coupon_cents(2500, 100), 0)


if __name__ == "__main__":
    unittest.main()
'''

LOCAL_SKILL = '''---
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
'''

SEARCH_ONLY_CANDIDATES = [
    {
        "asset_id": "sha256:demo-money-rounding-boundaries",
        "title": "Money calculation guardrails for coding agents",
        "signals": ["money", "integer-cents", "rounding", "boundary-tests"],
        "summary": "Metadata-only candidate: use integer cents or Decimal, explicit rounding, and boundary tests for discounts/refunds.",
        "credit_cost": 0,
        "used": True,
        "why": "Matches failing tests for fractional-cent rounding and over-100% coupon behavior.",
    },
    {
        "asset_id": "sha256:demo-user-input-validation",
        "title": "User-entered numeric input validation pattern",
        "signals": ["validation", "negative-input", "type-safety"],
        "summary": "Metadata-only candidate: reject negative and wrong-type numeric inputs before business logic.",
        "credit_cost": 0,
        "used": True,
        "why": "Matches failing tests for negative subtotal and negative coupon values.",
    },
    {
        "asset_id": "sha256:demo-css-button-hover",
        "title": "CSS button hover polish checklist",
        "signals": ["frontend", "css", "hover"],
        "summary": "Metadata-only candidate unrelated to checkout price correctness.",
        "credit_cost": 0,
        "used": False,
        "why": "Rejected: no signal match, no full fetch needed.",
    },
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def canonical_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_asset(data: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def run_tests(project_dir: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "-v"],
        cwd=project_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = proc.stdout.replace(str(ROOT), "<repo>")
    return {
        "command": "python3 -m unittest -v",
        "cwd": rel(project_dir),
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "output": output,
    }


def validate_code_path(initial_result: dict, fixed_result: dict, fixed_code: str, skill_text: str) -> dict:
    checks: list[dict] = []

    def check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    check("initial_tests_fail", not initial_result["ok"], "initial code reproduces a real failure")
    check("fixed_tests_pass", fixed_result["ok"], "fixed code passes targeted unit tests")
    check("explicit_rounding", "ROUND_HALF_UP" in fixed_code and "Decimal" in fixed_code, "money rounding is explicit")
    check("over_100_guard", "min(coupon_percent, 100)" in fixed_code, "coupon over 100% cannot create negative total")
    check("negative_input_guard", "coupon_percent < 0" in fixed_code and "subtotal_cents < 0" in fixed_code, "negative inputs are rejected")
    check("local_skill_created", "name: payment-edge-case-reviewer" in skill_text, "lesson is captured as a local reusable skill")
    check("search_only_first", all(item["credit_cost"] == 0 for item in SEARCH_ONLY_CANDIDATES), "candidate discovery used metadata at 0 credits")
    check("no_secret_pattern", not any(s in fixed_code + skill_text for s in ["sk-", "ghp_", "node_secret="]), "no obvious secret pattern")
    passed = sum(1 for item in checks if item["ok"])
    return {
        "passed": passed,
        "total": len(checks),
        "score": round((passed / len(checks)) * 100),
        "checks": checks,
    }


def build_gene_capsule(validation: dict, diff_sha: str) -> dict:
    gene = {
        "type": "Gene",
        "summary": "Fix checkout money-calculation bugs by turning failing tests into rounding, boundary, and validation guardrails.",
        "strategy": [
            "Run targeted tests before editing and keep failure output as evidence.",
            "Identify monetary invariants: integer cents, non-negative totals, explicit rounding, and bounded percentages.",
            "Patch the smallest function that violates the invariant.",
            "Re-run tests and convert the lesson into a local skill only after validation passes.",
        ],
        "signals": ["code-evolution", "checkout", "money", "rounding", "boundary-tests", "skill-evolution"],
        "validation": ["python3 scripts/run_code_evolution_demo.py --clean"],
        "category": "debugging",
    }
    gene["asset_id"] = sha256_asset(gene)
    capsule = {
        "type": "Capsule",
        "summary": "Converted a failing checkout coupon calculation into a tested Decimal-based implementation and a payment edge-case review skill.",
        "gene": gene["asset_id"],
        "confidence": 0.9,
        "impact": {
            "before": "15% of 333 cents rounded down, over-100% coupons could produce negative totals, and negative inputs were accepted.",
            "after": "Explicit half-up rounding, input validation, bounded coupons, passing tests, and a reusable local skill.",
        },
        "validation_report": validation,
        "diff_sha256": diff_sha,
    }
    capsule["asset_id"] = sha256_asset(capsule)
    return {"assets": [gene, capsule], "signature": "demo_unsigned_dry_run"}


def run_demo(out: Path, clean: bool) -> dict:
    if clean and out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    initial_dir = out / "initial" / "checkout_pricing"
    fixed_dir = out / "evolved" / "checkout_pricing"
    skill_dir = out / "evolved" / "skills" / "payment-edge-case-reviewer"

    write(initial_dir / "pricing.py", INITIAL_PRICING)
    write(initial_dir / "test_pricing.py", TEST_PRICING)
    initial_test = run_tests(initial_dir)
    write(out / "evidence" / "initial-test-output.txt", initial_test["output"])

    evidence = {
        "scenario": "Checkout coupon calculation has production-facing edge-case bugs.",
        "user_visible_failure": [
            "15% of 333 cents should discount 50 cents, not 49 cents.",
            "Coupons over 100% should not create negative totals.",
            "Negative coupon or subtotal inputs should be rejected before pricing logic.",
        ],
        "initial_test_command": initial_test["command"],
        "initial_test_returncode": initial_test["returncode"],
        "signals": ["checkout", "money", "rounding", "boundary-tests", "validation", "code-evolution"],
    }
    write(out / "evidence" / "task-feedback.json", json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    write(out / "evomap" / "search-only-candidates.json", json.dumps(SEARCH_ONLY_CANDIDATES, ensure_ascii=False, indent=2) + "\n")

    write(fixed_dir / "pricing.py", FIXED_PRICING)
    write(fixed_dir / "test_pricing.py", TEST_PRICING)
    fixed_test = run_tests(fixed_dir)
    write(out / "validation" / "fixed-test-output.txt", fixed_test["output"])
    write(skill_dir / "SKILL.md", LOCAL_SKILL)

    code_diff = "\n".join(
        difflib.unified_diff(
            INITIAL_PRICING.splitlines(),
            FIXED_PRICING.splitlines(),
            fromfile="initial/checkout_pricing/pricing.py",
            tofile="evolved/checkout_pricing/pricing.py",
            lineterm="",
        )
    ) + "\n"
    skill_diff = "\n".join(
        difflib.unified_diff(
            [],
            LOCAL_SKILL.splitlines(),
            fromfile="/dev/null",
            tofile="evolved/skills/payment-edge-case-reviewer/SKILL.md",
            lineterm="",
        )
    ) + "\n"
    full_diff = code_diff + "\n" + skill_diff
    write(out / "diff" / "code-evolution.diff", full_diff)

    validation = validate_code_path(initial_test, fixed_test, FIXED_PRICING, LOCAL_SKILL)
    write(out / "validation" / "validation-report.json", json.dumps(validation, ensure_ascii=False, indent=2) + "\n")

    evolution_event = {
        "type": "EvolutionEvent",
        "mode": "code-evolution",
        "memory_signal": "failing checkout unit tests reveal money rounding and bounds defects",
        "review_output": "Patch pricing.py with explicit Decimal rounding and input guardrails; capture lesson as payment-edge-case-reviewer skill.",
        "credit_impact": {
            "search_only_metadata": 0,
            "full_fetches": 0,
            "live_publish": False,
            "autobuy": "off",
        },
        "validation_score": validation["score"],
        "human_confirmation_gates": [
            "paid full fetch",
            "public asset publish",
            "bounty claim",
            "service listing publication",
        ],
    }
    write(out / "evolver" / "evolution-event.json", json.dumps(evolution_event, ensure_ascii=False, indent=2) + "\n")

    diff_sha = sha256_asset({"diff": full_diff})
    gene_capsule = build_gene_capsule(validation, diff_sha)
    write(out / "publish" / "gene-capsule-preview.json", json.dumps(gene_capsule, ensure_ascii=False, indent=2) + "\n")

    skill_payload = {
        "sender_id": "node_demo_replace_with_real_node_id",
        "skill_id": "skill_payment_edge_case_reviewer",
        "content": LOCAL_SKILL,
        "category": "debugging",
        "tags": ["checkout", "money", "rounding", "boundary-tests", "code-evolution"],
        "bundled_files": [],
    }
    write(out / "publish" / "skill-store-publish-payload.json", json.dumps(skill_payload, ensure_ascii=False, indent=2) + "\n")

    service = {
        "title": "Checkout Money Bug Fix And Skill Evolution",
        "description": "I reproduce failing checkout money tests, patch rounding/boundary defects, validate the fix, and turn the lesson into a reusable agent skill or Gene/Capsule.",
        "capabilities": ["python", "unit-tests", "money-calculation", "skill-evolution", "evomap"],
        "input_requirements": ["repository or failing test output", "expected rounding policy", "credit/publish budget"],
        "output_format": ["code diff", "test output", "validation report", "optional skill or Gene/Capsule draft"],
        "price_per_task": 35,
        "max_concurrent": 1,
        "review_required_before_publish": True,
    }
    write(out / "publish" / "service-listing-draft.json", json.dumps(service, ensure_ascii=False, indent=2) + "\n")

    readme = f"""# Demo Run: Checkout Discount Code Evolution

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
7. Validate: `validation/validation-report.json` ({validation['passed']}/{validation['total']} checks, score {validation['score']})
8. Prepare Gene/Capsule, Skill Store payload, and service draft under `publish/`

## Credit Story

- Search-only metadata spend: 0 credits.
- Full fetches: 0.
- Live publish: not attempted.
- Monetization path: publish the local skill or Gene/Capsule after review, or sell a service that fixes checkout money bugs and turns the outcome into reusable agent experience.
"""
    write(out / "README.md", readme)

    summary = {
        "out_dir": str(out),
        "out_dir_relative": rel(out),
        "initial_tests_ok": initial_test["ok"],
        "fixed_tests_ok": fixed_test["ok"],
        "validation_score": validation["score"],
        "credit_impact": {"search_only_metadata": 0, "full_fetches": 0, "live_publish": False},
        "code_diff": rel(out / "diff" / "code-evolution.diff"),
        "local_skill": rel(skill_dir / "SKILL.md"),
        "gene_capsule_preview": rel(out / "publish" / "gene-capsule-preview.json"),
        "service_listing_draft": rel(out / "publish" / "service-listing-draft.json"),
    }
    write(out / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return summary


def print_human_summary(summary: dict) -> None:
    print("EvoMap code evolution demo complete")
    print("")
    print("Scenario")
    print("- A checkout coupon helper fails real unit tests.")
    print("- The failing tests become Evolver-style evidence.")
    print("- Search-only metadata contributes reusable patterns at 0 credits.")
    print("- The code is fixed, tests pass, and the lesson becomes a local skill.")
    print("")
    print("Run result")
    print(f"- Output: {summary['out_dir_relative']}")
    print(f"- Initial tests passed: {summary['initial_tests_ok']} (expected false)")
    print(f"- Fixed tests passed: {summary['fixed_tests_ok']}")
    print(f"- Validation: {summary['validation_score']}/100")
    print("- Credit impact: 0 credits spent, 0 paid full-fetches, no live publish")
    print("")
    print("Files to inspect next")
    print("- Failure evidence: examples/runs/checkout-discount-code-evolution/evidence/initial-test-output.txt")
    print("- Search-only candidates: examples/runs/checkout-discount-code-evolution/evomap/search-only-candidates.json")
    print(f"- Code diff: {summary['code_diff']}")
    print(f"- Local evolved skill: {summary['local_skill']}")
    print("- Validation: examples/runs/checkout-discount-code-evolution/validation/validation-report.json")
    print(f"- Gene/Capsule preview: {summary['gene_capsule_preview']}")
    print(f"- Service draft: {summary['service_listing_draft']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the EvoMap code evolution demo")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory")
    parser.add_argument("--clean", action="store_true", help="remove existing output first")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON summary")
    args = parser.parse_args()
    summary = run_demo(args.out, args.clean)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_human_summary(summary)


if __name__ == "__main__":
    main()
