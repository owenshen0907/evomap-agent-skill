#!/usr/bin/env python3
"""Run a deterministic EvoMap skill-evolution demo.

This script demonstrates the core story for the handbook:
1. A Codex user owns a simple local skill.
2. A real task produces feedback/evidence.
3. The skill evolves from that evidence.
4. The evolved skill is packaged for EvoMap Skill Store publishing.
5. Optional live publish is available only with explicit flags and credentials.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from urllib import request, error

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "examples" / "runs" / "codex-pr-review-skill"
HUB = "https://evomap.ai"

INITIAL_SKILL = """---
name: codex-pr-reviewer
description: Review code changes and summarize likely issues for a user.
---

# Codex PR Reviewer

## Workflow

1. Read the diff.
2. Identify likely bugs.
3. Summarize the change.
4. Suggest tests when useful.
"""

EVIDENCE = {
    "scenario": "Codex reviews a pull request that adds a risky database cleanup migration.",
    "user_prompt": "Review this PR. It adds a cleanup migration and changes the account deletion flow.",
    "original_skill_version": "0.1.0",
    "task_outcome": "User rejected the review as too shallow.",
    "feedback": [
        "The review summarized the diff before findings, making real risks hard to see.",
        "It did not require git status before reading the diff, so untracked migration files could be missed.",
        "It missed that the migration deletes rows without a rollback strategy.",
        "It did not ask whether destructive commands or production data operations were allowed.",
        "It suggested generic tests instead of a concrete migration rollback / fixture test.",
    ],
    "signals": [
        "codex",
        "code-review",
        "git-safety",
        "database-migration",
        "destructive-change",
        "missing-tests",
        "skill-evolution",
    ],
    "validation_command": "python3 scripts/run_skill_evolution_demo.py --check examples/runs/codex-pr-review-skill/evolved/codex-pr-reviewer/SKILL.md",
}

SEARCH_ONLY_CANDIDATES = [
    {
        "asset_id": "sha256:demo-metadata-git-safety",
        "title": "Git safety preflight for coding agents",
        "signals": ["git-safety", "dirty-worktree", "destructive-command"],
        "summary": "Metadata-only candidate: require git status, classify unrelated changes, and avoid destructive commands without confirmation.",
        "credit_cost": 0,
        "used": True,
        "why": "Matches the missed preflight and destructive-change feedback.",
    },
    {
        "asset_id": "sha256:demo-metadata-review-findings",
        "title": "Findings-first review output contract",
        "signals": ["code-review", "findings-first", "line-references"],
        "summary": "Metadata-only candidate: order findings by severity and keep summary secondary.",
        "credit_cost": 0,
        "used": True,
        "why": "Matches the user's complaint that summaries hid the risks.",
    },
    {
        "asset_id": "sha256:demo-metadata-ui-copy",
        "title": "UI copy polish checklist",
        "signals": ["frontend", "copywriting"],
        "summary": "Metadata-only candidate unrelated to database migration review.",
        "credit_cost": 0,
        "used": False,
        "why": "Rejected: weak signal match, no need for full fetch.",
    },
]

EVOLVED_SKILL = """---
name: codex-pr-reviewer
description: Review code changes for bugs, regressions, migration risk, missing tests, and git-safety issues. Use when Codex is asked to review a PR, diff, branch, migration, cleanup job, destructive change, or suspicious worktree state; prioritize findings with file/line references before summaries.
---

# Codex PR Reviewer

## Goal

Find actionable risks before summarizing the change. Protect the user's worktree and reputation by separating evidence, assumptions, and safe next actions.

## Preflight

1. Run `git status --short` and identify tracked, untracked, staged, and unrelated files.
2. Inspect the diff relevant to the requested review; do not revert or overwrite unrelated user changes.
3. If migrations, deletion jobs, data backfills, auth changes, billing changes, or destructive commands appear, mark the review as high-risk.
4. Do not run destructive commands, production data operations, or networked publish actions without explicit confirmation.

## Review Workflow

1. Read changed files and tests before forming conclusions.
2. List findings first, ordered by severity.
3. Include tight file/line references when possible.
4. For each finding, explain the user-visible failure mode, not just the code smell.
5. Add a short testing gap section when validation is missing or too generic.
6. Keep the final summary secondary and brief.

## Migration And Destructive-Change Checks

- Check whether deletes, drops, truncates, irreversible migrations, or cleanup jobs have rollback or dry-run paths.
- Look for idempotency, batching, locks, timeouts, and observability on data changes.
- Require fixture tests for data transformations and rollback/abort behavior when applicable.
- If production data could be touched, ask for explicit environment and approval boundaries.

## Output Contract

Use this structure:

```text
Findings
- [P1/P2/P3] File:line — issue, impact, and fix direction.

Open Questions
- Only questions that change the review outcome.

Testing Gaps
- Concrete missing tests or commands.

Summary
- 1-3 lines after findings.
```

## Reference Checklist

When the review involves migrations or destructive changes, load `references/review-checklist.md`.
"""

REVIEW_CHECKLIST = """# Review Checklist

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
"""


def canonical_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_asset(data: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_skill(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    checks = []

    def check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    check("frontmatter", text.startswith("---\n") and "\n---\n" in text[4:], "YAML frontmatter exists")
    check("name", "name: codex-pr-reviewer" in text, "skill name is stable")
    check("description", "description:" in text and "migration" in text.lower(), "description includes trigger signals")
    check("preflight", "## Preflight" in text and "git status --short" in text, "git preflight is required")
    check("findings_first", "Findings" in text and "ordered by severity" in text, "findings-first contract exists")
    check("destructive_guardrail", "destructive" in text.lower() and "explicit confirmation" in text.lower(), "destructive actions require confirmation")
    check("reference", "references/review-checklist.md" in text, "long checklist is in a reference")
    check("no_fake_secret", not any(s in text for s in ["sk-", "ghp_", "node_secret="]), "no obvious secret pattern")
    passed = sum(1 for item in checks if item["ok"])
    return {
        "path": str(path),
        "passed": passed,
        "total": len(checks),
        "score": round((passed / len(checks)) * 100),
        "checks": checks,
    }


def build_publish_payload(evolved_skill: str) -> dict:
    return {
        "sender_id": "node_demo_replace_with_real_node_id",
        "skill_id": "skill_codex_pr_reviewer_git_safety",
        "content": evolved_skill,
        "category": "optimize",
        "tags": ["codex", "code-review", "git-safety", "migration", "skill-evolution"],
        "bundled_files": [
            {"name": "references/review-checklist.md", "content": REVIEW_CHECKLIST},
        ],
    }


def build_gene_capsule(validation: dict, publish_payload: dict) -> dict:
    gene = {
        "type": "Gene",
        "summary": "Improve Codex review skills using feedback-driven git safety and migration risk guardrails.",
        "strategy": [
            "Collect task feedback and identify missed review signals.",
            "Patch skill triggers and workflow guardrails.",
            "Move long checklists into references.",
            "Validate frontmatter, output contract, and no-secret constraints.",
            "Package the evolved skill for EvoMap Skill Store review.",
        ],
        "validation": ["python3 scripts/run_skill_evolution_demo.py --check <path-to-SKILL.md>"],
        "signals": EVIDENCE["signals"],
        "category": "optimize",
    }
    gene["asset_id"] = sha256_asset(gene)
    capsule = {
        "type": "Capsule",
        "summary": "Evolved codex-pr-reviewer from a shallow review skill into a findings-first, git-safe, migration-aware review skill.",
        "gene": gene["asset_id"],
        "confidence": 0.86,
        "signals": EVIDENCE["signals"],
        "impact": {
            "before": "Summarized diffs and suggested generic tests.",
            "after": "Requires git preflight, findings-first output, destructive-change guardrails, and concrete migration tests.",
        },
        "validation_report": validation,
        "skill_store_payload_sha256": sha256_asset(publish_payload),
    }
    capsule["asset_id"] = sha256_asset(capsule)
    return {"assets": [gene, capsule], "signature": "demo_unsigned_dry_run"}


def maybe_publish(payload: dict, yes: bool) -> dict:
    node_id = os.environ.get("EVOMAP_NODE_ID") or os.environ.get("A2A_NODE_ID")
    node_secret = os.environ.get("EVOMAP_NODE_SECRET") or os.environ.get("A2A_NODE_SECRET")
    if not yes:
        return {"ok": False, "skipped": True, "reason": "dry_run_default", "endpoint": f"{HUB}/a2a/skill/store/publish"}
    if not node_id or not node_secret:
        return {"ok": False, "skipped": True, "reason": "missing_EVOMAP_NODE_ID_or_SECRET"}
    live_payload = {**payload, "sender_id": node_id}
    req = request.Request(
        f"{HUB}/a2a/skill/store/publish",
        data=json.dumps(live_payload).encode("utf-8"),
        headers={"content-type": "application/json", "authorization": f"Bearer {node_secret}"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return {"ok": True, "status": resp.status, "response": json.loads(body) if body else {}}
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return {"ok": False, "status": exc.code, "response": parsed}


def run_demo(out: Path, clean: bool, publish: bool) -> dict:
    if clean and out.exists():
        for child in sorted(out.rglob("*"), reverse=True):
            if child.is_file() or child.is_symlink():
                child.unlink()
            elif child.is_dir():
                child.rmdir()
    out.mkdir(parents=True, exist_ok=True)

    initial_dir = out / "initial" / "codex-pr-reviewer"
    evolved_dir = out / "evolved" / "codex-pr-reviewer"
    write(initial_dir / "SKILL.md", INITIAL_SKILL)
    write(out / "evidence" / "task-feedback.json", json.dumps(EVIDENCE, ensure_ascii=False, indent=2) + "\n")
    write(out / "evomap" / "search-only-candidates.json", json.dumps(SEARCH_ONLY_CANDIDATES, ensure_ascii=False, indent=2) + "\n")

    write(evolved_dir / "SKILL.md", EVOLVED_SKILL)
    write(evolved_dir / "references" / "review-checklist.md", REVIEW_CHECKLIST)

    diff = "\n".join(difflib.unified_diff(
        INITIAL_SKILL.splitlines(),
        EVOLVED_SKILL.splitlines(),
        fromfile="initial/codex-pr-reviewer/SKILL.md",
        tofile="evolved/codex-pr-reviewer/SKILL.md",
        lineterm="",
    )) + "\n"
    write(out / "diff" / "skill-evolution.diff", diff)

    validation = validate_skill(evolved_dir / "SKILL.md")
    write(out / "validation" / "validation-report.json", json.dumps(validation, ensure_ascii=False, indent=2) + "\n")

    publish_payload = build_publish_payload(EVOLVED_SKILL)
    write(out / "publish" / "skill-store-publish-payload.json", json.dumps(publish_payload, ensure_ascii=False, indent=2) + "\n")
    curl_script = """#!/usr/bin/env bash
set -euo pipefail
: "${EVOMAP_NODE_ID:?Set EVOMAP_NODE_ID}"
: "${EVOMAP_NODE_SECRET:?Set EVOMAP_NODE_SECRET}"
python3 - <<'PY' > /tmp/evomap-skill-payload.json
import json
import os
from pathlib import Path
payload=json.loads(Path('publish/skill-store-publish-payload.json').read_text())
payload['sender_id']=os.environ['EVOMAP_NODE_ID']
print(json.dumps(payload, ensure_ascii=False))
PY
curl -sS -X POST https://evomap.ai/a2a/skill/store/publish \
  -H "Authorization: Bearer ${EVOMAP_NODE_SECRET}" \
  -H "Content-Type: application/json" \
  --data @/tmp/evomap-skill-payload.json
"""
    write(out / "publish" / "publish-skill-store.sh", curl_script)

    service = {
        "title": "Codex PR Review Skill Evolution",
        "description": "I improve a user's Codex review skill from real review feedback, add git-safety and migration-risk guardrails, validate the skill, and package it for EvoMap Skill Store publishing.",
        "capabilities": ["skill-evolution", "codex", "code-review", "git-safety", "migration-risk"],
        "use_cases": [
            "A review skill misses destructive migration risk",
            "A Codex workflow needs findings-first review output",
            "A team wants to package a repeated review pattern as a public skill",
        ],
        "price_per_task": 30,
        "max_concurrent": 1,
        "review_required_before_publish": True,
    }
    write(out / "publish" / "service-listing-draft.json", json.dumps(service, ensure_ascii=False, indent=2) + "\n")

    bundle = build_gene_capsule(validation, publish_payload)
    write(out / "publish" / "gene-capsule-preview.json", json.dumps(bundle, ensure_ascii=False, indent=2) + "\n")

    publish_result = maybe_publish(publish_payload, publish)
    write(out / "publish" / "live-publish-result.json", json.dumps(publish_result, ensure_ascii=False, indent=2) + "\n")

    timeline = f"""# Demo Run: Codex PR Review Skill Evolution

Generated at: {datetime.now(timezone.utc).isoformat()}

## Core Scenario

A user has a simple Codex review skill. It fails on a database cleanup migration review because it summarizes first, misses git preflight, and does not guard destructive data changes. EvoMap-style metadata search contributes reusable patterns without spending credits. The skill evolves, validates, and is packaged for EvoMap Skill Store publishing.

## Steps

1. Seed local skill: `initial/codex-pr-reviewer/SKILL.md`
2. Capture task feedback: `evidence/task-feedback.json`
3. Search metadata only: `evomap/search-only-candidates.json` (0 credits)
4. Evolve skill: `evolved/codex-pr-reviewer/SKILL.md`
5. Validate: `validation/validation-report.json` ({validation['passed']}/{validation['total']} checks, score {validation['score']})
6. Package Skill Store payload: `publish/skill-store-publish-payload.json`
7. Prepare Gene/Capsule preview: `publish/gene-capsule-preview.json`
8. Prepare service listing: `publish/service-listing-draft.json`

## Credit Story

- Search-only metadata spend: 0 credits.
- Full fetches: 0.
- Live publish: {'attempted' if publish else 'not attempted; dry-run package generated'}.
- Monetization path: publish skill for distribution, sell the service for repeated skill evolution work, and earn credits through bounties or asset reuse when accepted by EvoMap quality gates.

## Human Confirmation Gates

- Publish to Skill Store requires real `EVOMAP_NODE_ID` / `EVOMAP_NODE_SECRET` and explicit `--publish`.
- Public visibility, paid full fetch, bounty claim, and service publication remain manual decisions.
"""
    write(out / "README.md", timeline)

    summary = {
        "out_dir": str(out),
        "validation_score": validation["score"],
        "publish_payload": str(out / "publish" / "skill-store-publish-payload.json"),
        "live_publish": publish_result,
        "evolved_skill": str(evolved_dir / "SKILL.md"),
        "diff": str(out / "diff" / "skill-evolution.diff"),
    }
    write(out / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the EvoMap skill evolution demo")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory")
    parser.add_argument("--clean", action="store_true", help="remove existing output first")
    parser.add_argument("--publish", action="store_true", help="attempt live Skill Store publish; requires EVOMAP_NODE_ID and EVOMAP_NODE_SECRET")
    parser.add_argument("--check", type=Path, help="validate a skill file and exit")
    args = parser.parse_args()
    if args.check:
        print(json.dumps(validate_skill(args.check), ensure_ascii=False, indent=2))
        return
    summary = run_demo(args.out, args.clean, args.publish)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
