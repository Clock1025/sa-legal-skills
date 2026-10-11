#!/usr/bin/env python3
"""Dependency-free structural checks for sa-legal-skills.

These checks are NOT legal accuracy, DOCX rendering, or live model-behavior tests.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("regulation-review", "large-scale-reform", "amendment-drafting")
issues = []

def check_file(relative_path: str, required_phrases=()):
    path = ROOT / relative_path
    if not path.is_file():
        issues.append(f"Missing file: {relative_path}")
        return
    content = path.read_text(encoding="utf-8-sig")
    if not content.strip():
        issues.append(f"Empty file: {relative_path}")
    for phrase in required_phrases:
        if phrase not in content:
            issues.append(f"{relative_path}: missing required reference {phrase!r}")

check_file("README.md", [f"skills/{skill}/SKILL.md" for skill in SKILLS])
check_file("START-HERE.md", list(SKILLS) + ["完整讀取"])
for skill in SKILLS:
    check_file(f"skills/{skill}/SKILL.md")
check_file("LICENSE")
check_file("scripts/package-release.sh")

if issues:
    print("Repository structural validation FAILED:")
    for issue in issues:
        print(f"  - {issue}")
    sys.exit(1)

print("Repository structural validation PASSED.")
print("Limit: no live-model inference, legal correctness, or DOCX compliance was tested.")
