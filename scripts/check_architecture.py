#!/usr/bin/env python3
import sys
from pathlib import Path

# Architectural Linter
# Enforces Constitution §6.8 (Locality) and §5.3 (Boundaries)
# Prevents "Domain" from becoming "Infrastructure"

RED = "\033[0;31m"
GREEN = "\033[0;32m"
NC = "\033[0m"

VIOLATIONS = []


def report_violation(file_path: Path, illegal_import: str, rule: str) -> None:
    VIOLATIONS.append(
        f"{RED}❌ [Arch Violation] {file_path}{NC}\n"
        f"   Imported: {illegal_import}\n"
        f"   Rule: {rule}"
    )


def check_haskell_file(file_path: Path) -> None:
    content = file_path.read_text()

    # 1. Domain Isolation Rule
    # Domain modules MUST NOT import Effect, App, or specific external IO libs
    if "src/Domain" in str(file_path):
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if not line.startswith("import"):
                continue

            # Forbidden internal layers
            if "import Effect" in line:
                report_violation(
                    file_path,
                    line,
                    "Domain MUST NOT import Effect (Inversion of Control)",
                )
            if "import App" in line:
                report_violation(
                    file_path, line, "Domain MUST NOT import App (Circular Dependency)"
                )
            if "import Workflow" in line:
                report_violation(
                    file_path, line, "Domain MUST NOT import Workflow (Layering)"
                )

            # Forbidden IO libraries in Domain (Partial list of dangerous ones)
            if "import Network.HTTP" in line:
                report_violation(file_path, line, "Domain MUST be pure (No HTTP)")
            if "import Database" in line:
                report_violation(file_path, line, "Domain MUST be pure (No DB)")
            if "import System.IO" in line:
                report_violation(file_path, line, "Domain MUST be pure (No System.IO)")


def check_elm_file(file_path: Path) -> None:
    content = file_path.read_text()

    # 1. Domain Isolation Rule
    if "src/Domain" in str(file_path):
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if not line.startswith("import"):
                continue

            if "import Http" in line:
                report_violation(file_path, line, "Domain MUST be pure (No Http)")
            if "import Json.Decode" in line:
                report_violation(
                    file_path, line, "Domain MUST be pure (No Decoders - use Api/)"
                )
            if "import Effect" in line:
                report_violation(file_path, line, "Domain MUST NOT import Effect")
            if "import Pages" in line:
                report_violation(file_path, line, "Domain MUST NOT import Pages")


def check_architecture() -> None:
    print("🏰 Scanning Architectural Boundaries...")

    # Walk through src/ looking for .hs and .elm files
    root = Path(".")

    for path in root.rglob("*"):
        if path.is_file():
            if path.suffix == ".hs":
                check_haskell_file(path)
            elif path.suffix == ".elm":
                check_elm_file(path)

    if VIOLATIONS:
        print(f"\n{len(VIOLATIONS)} Architectural Violations Found:\n")
        for v in VIOLATIONS:
            print(v)
        sys.exit(1)
    else:
        print(f"{GREEN}✅ Architecture compliant (Domain is pure).{NC}")


if __name__ == "__main__":
    check_architecture()
