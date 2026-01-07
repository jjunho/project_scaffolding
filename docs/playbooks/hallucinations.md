# Hallucination Log (AI Error Patterns)

> **PURPOSE**: Record specific, recurring AI failure modes, package hallucinations, or anti-patterns to prevent repetition. Reference this during "Assumption Resets".

## 1. Package & Library Hallucinations
- **Pattern**: AI tries to use `Data.String.Utils` (Haskell).
  - **Correction**: Use `Data.Text` and `Data.Text.Encoding`.
- **Pattern**: AI hallucinated the GHC flag `-Wredundant-brackets`.
  - **Correction**: This flag does not exist in GHC 9.10.3. Style-based checks like redundant brackets are handled by **HLint**, not the compiler.
- **Pattern**: AI tries to use `elm-community/json-extra` without verification.
  - **Correction**: Check `elm.json` first; prefer standard `Json.Decode`.

## 2. Structural Hallucinations
- **Pattern**: AI attempts to "fix" circular imports by adding an intermediate "Manager" or "Service" class.
  - **Correction**: This is an anti-pattern. Refactor into pure data transformations and push the circularity to the `Workflow` or `App` layer.
- **Pattern**: AI assumes Python scripts can use relative imports without a `__init__.py` or `src` layout.
  - **Correction**: Project uses a strict `src` layout. Use absolute imports.

## 3. Constitutional Drift
- **Pattern**: AI "silently" adds `do` notation to pure functions to make them look "more functional".
  - **Correction**: Use composition (`.`) and (`$`). `do` notation is for effects.
- **Pattern**: AI attempts to bypass `scripts/check_architecture.py` by using polymorphic types to hide IO.
  - **Correction**: Audit type signatures in PR review for "God Monads" (`ReaderT Env IO`).

## 4. Process & Tooling Failures
- **Pattern**: Manual Fix Over Tooling (Ignoring the Teachers).
  - **Mistake**: AI treats compiler/linter errors as obstacles to bypass manually instead of lessons to learn from. This includes trying to hand-fix things that `ruff`, `elm-format`, `hlint`, or `ormolu` can do automatically, or ignoring the specific "how-to-fix" guidance provided by GHC and the Elm compiler.
  - **Correction**: Compilers (GHC, Elm) and Linters (HLint, Ruff, Clippy) are TEACHERS. They provide the most accurate path to correctness. 
    1. Read the ENTIRE error message; they often contain the exact solution.
    2. Use automated fixers (`ruff --fix`, `hlint --refactor`, etc.) as the first line of defense.
    3. Trust the tooling's diagnostic power over your own intuition when they conflict.
    4. "Do not do by yourself what the tool can do for you."

- **Pattern**: Push-and-Pray CI Fixes.
  - **Mistake**: Making multiple "guess-and-check" commits to resolve CI environment issues (paths, missing tools, etc.) instead of simulating the CI environment locally. This pollutes the git log and wastes CI resources.
  - **Correction**: If CI fails, **STOP**. Recreate the failure locally using `act` or a raw Docker container (`docker run --rm -v $(pwd):/app ...`). Verify the `Makefile` and environment setup in that container. Only push when the local simulation passes.

## 5. Integrity Failures
- **Pattern**: Fabrication / Lying.
  - **Mistake**: AI invents a library, a file path, or a capability that does not exist to "satisfy" the user's request.
  - **Correction**: **Stop, Verify, and Admit Ignorance.**
    - If you are not 100% sure a library exists, **check it** (via search or repl).
    - If you do not know the answer, say "I do not know."
    - Refer to **Constitution §6.11 (No Fabrication)**.
