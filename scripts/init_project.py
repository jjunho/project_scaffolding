#!/usr/bin/env python3
import shutil
import sys
from pathlib import Path

# Project Initializer
# Renames the project components and updates references.
# Usage: ./scripts/init_project.py <new_backend_name> <new_frontend_name>


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: init_project.py <backend_name> <frontend_name>", file=sys.stderr)
        sys.exit(1)

    backend_name = sys.argv[1]
    frontend_name = sys.argv[2]
    root = Path(".")

    print(
        f"🚀 Initializing project: Backend='{backend_name}', Frontend='{frontend_name}'"
    )

    # 1. Rename Directories
    src = root / "src"
    if (src / "backend").exists():
        print(f"Moving src/backend -> src/{backend_name}")
        shutil.move(src / "backend", src / backend_name)

    if (src / "frontend").exists():
        print(f"Moving src/frontend -> src/{frontend_name}")
        shutil.move(src / "frontend", src / frontend_name)

    # 2. Update Root Makefile (COMPONENTS list)
    # The Makefile logic `MODULES ?= $(patsubst src/%/,%,$(dir $(wildcard src/*/)))`
    # is dynamic, so it should auto-detect the change!
    print("✅ Makefile auto-detects components. No change needed.")

    # 3. Update Haskell Package Name (in package.yaml)
    # This is trickier as we need to parse/replace content.
    # For a scaffold, we advise the user to do this part manually or use
    # stack/cabal tools, as search/replace on 'backend' might be too aggressive.
    print(f"⚠️  Manual Step: Rename 'name: backend' in src/{backend_name}/package.yaml")
    print(
        f"⚠️  Manual Step: Rename 'name: frontend' in "
        f"src/{frontend_name}/package.json (if applicable)"
    )

    print("\n✅ Initialization complete. Run 'make status' to verify.")


if __name__ == "__main__":
    main()
