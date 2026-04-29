#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "evomap-agent-economy" / "SKILL.md"
REQUIRED = [
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "docs" / "AGENT_GUIDE.zh.md",
    ROOT / "docs" / "FEISHU_DOC_DRAFT.zh.md",
    ROOT / "docs" / "OPERATIONS_FAQ.zh.md",
    ROOT / "docs" / "OFFICIAL_EVOLVER_SELF_EVOLUTION.zh.md",
    ROOT / "docs" / "CORE_SCENARIO.zh.md",
    ROOT / "docs" / "CODE_EVOLUTION_SCENARIO.zh.md",
    ROOT / "scripts" / "run_skill_evolution_demo.py",
    ROOT / "scripts" / "run_code_evolution_demo.py",
    SKILL,
    ROOT / "skills" / "evomap-agent-economy" / "agents" / "openai.yaml",
    ROOT / "skills" / "evomap-agent-economy" / "references" / "core-concepts.md",
    ROOT / "skills" / "evomap-agent-economy" / "references" / "platform-install.md",
    ROOT / "skills" / "evomap-agent-economy" / "references" / "credit-flywheel.md",
    ROOT / "skills" / "evomap-agent-economy" / "references" / "skill-self-improvement.md",
    ROOT / "skills" / "evomap-agent-economy" / "references" / "bounty-service-playbook.md",
    ROOT / "skills" / "evomap-agent-economy" / "references" / "operations-faq.md",
    ROOT / "skills" / "evomap-agent-economy" / "references" / "official-evolver-self-evolution.md",
]

errors = []
for path in REQUIRED:
    if not path.exists():
        errors.append(f"missing: {path.relative_to(ROOT)}")

if SKILL.exists():
    text = SKILL.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append("SKILL.md frontmatter is not closed")
    else:
        front = match.group(1)
        if "name: evomap-agent-economy" not in front:
            errors.append("SKILL.md frontmatter must include name: evomap-agent-economy")
        if "description:" not in front:
            errors.append("SKILL.md frontmatter must include description")
    if "node_secret" not in text:
        errors.append("SKILL.md should explicitly guard node_secret")

secret_patterns = [
    r"sk-[A-Za-z0-9]{20,}",
    r"ghp_[A-Za-z0-9]{20,}",
    r"xox[baprs]-[A-Za-z0-9-]{20,}",
]
for path in ROOT.rglob("*"):
    if path.is_dir() or ".git" in path.parts:
        continue
    if path.suffix.lower() not in {".md", ".yaml", ".yml", ".txt", ".py", ".mdc"}:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pat in secret_patterns:
        if re.search(pat, text):
            errors.append(f"possible secret pattern in {path.relative_to(ROOT)}")

if errors:
    print("Validation failed:")
    for err in errors:
        print(f"- {err}")
    sys.exit(1)

print("Validation passed.")
