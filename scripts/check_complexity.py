#!/usr/bin/env python3
import re
import sys
from pathlib import Path

# Complexity & Hygiene Linter
# Enforces:
# 1. Constitution §6.7 (Anti-Complexity): No files > 500 LOC.
# 2. Strict TO-DOs: No bare 'TO-DO' without ownership.

RED = "\033[0;31m"
GREEN = "\033[0;32m"
NC = "\033[0m"

MAX_LOC = 500
# Matches TODO(user) or FIXME(#123)
# Negative lookahead checks that it's NOT followed by (
# We split the string to avoid self-flagging by this very script
TODO_PATTERN = re.compile(r"\b(TO" + r"DO|FIX" + r"ME)\b(?!\()")

VIOLATIONS = []


def check_file(path: Path) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return  # Skip binary files

    # 1. LOC Check
    if len(lines) > MAX_LOC:
        VIOLATIONS.append(
            f"{RED}❌ [Too Large] {path}: {len(lines)} lines (Max: {MAX_LOC}){NC}\n"
            f"   → AI Context Risk: Split this file immediately."
        )

    # 2. Strict TO-DO Check
    for i, line in enumerate(lines, 1):
        if TODO_PATTERN.search(line):
            VIOLATIONS.append(
                f"{RED}❌ [Bare TO-DO] {path}:{i}{NC}\n"
                f"   → Found '{line.strip()}'\n"
                f"   → Rule: Must use TODO(user) or TODO(#issue)"
            )


def check_hygiene() -> None:
    print("🔍 Scanning for Complexity and Hygiene...")

    root = Path(".")
    # Scan src/ and scripts/
    targets = list(root.glob("src/**/*")) + list(root.glob("scripts/**/*"))

    for path in targets:
        if path.is_file() and path.suffix in [".py", ".hs", ".elm"]:
            check_file(path)

    if VIOLATIONS:
        print(f"\n{len(VIOLATIONS)} Hygiene Violations Found:\n")
        for v in VIOLATIONS:
            print(v)
        sys.exit(1)
    else:
        print(f"{GREEN}✅ Hygiene compliant (No God Files, Strict TODOs).{NC}")


if __name__ == "__main__":
    check_hygiene()
