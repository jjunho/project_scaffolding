# AI Context Map (Machine-Optimized)

**ROLE**: You are an expert software engineer working in a strictly governed repository.
**GOAL**: Write code that passes `make check` on the first try and adheres to the Constitution.

## 1. The Constitution (Summary)
*   **Authority**: `docs/CONSTITUTION.md` is supreme.
*   **AI Risk**: You are "untrusted input". Your output MUST be verifiable.
*   **Verification**: If you write code, you MUST provide a verification command (e.g., `make test`).
*   **Loop Guard**: If compilation fails TWICE, you MUST STOP and read `docs/playbooks/compiler-loops.md`.
*   **Simplicity**: Prefer the simplest correct solution. No speculative abstraction.
*   **Forbidden**:
    *   `Debug.log` / `print()` in production code.
    *   Circular dependencies.
    *   "Manager/Controller" classes (Anti-pattern).
    *   Blindly copying OOP patterns into FP languages (Haskell/Elm).

## 2. Project Structure & Interface
*   **Root**: `/home/jjunho/proj`
*   **Entry Point**: `Makefile` is the canonical interface.
    *   `make check`: The ONE gate you must pass (fmt + lint + test + build).
    *   `make fmt`: Fixes formatting.
    *   `make lint`: Checks for static errors.
    *   `make hooks`: Installs git hooks.
*   **Structure**:
    *   `src/`: Application code (components).
    *   `scripts/`: Python/Bash automation.
    *   `docs/`: Standards and ADRs.
    *   `ci/`: CI configurations.

## 3. Language Rules (Strict)

### Python (`docs/standards/languages/python.md`)
*   **Type Hints**: MANDATORY for all function arguments/returns.
*   **Tools**: `ruff` (lint), `black` (fmt), `mypy` (types).
*   **Forbidden**: `print()` (use logging), implicit globals, `from module import *`.
*   **Error Handling**: No bare `except:`. Define custom exceptions.

### Haskell (`docs/standards/languages/haskell.md`)
*   **No OOP**: No "Service" objects. Use pure functions and ADTs.
*   **No Partiality**: `head`, `tail`, `!!` are BANNED.
*   **State**: Use ADTs, not Boolean soup (`isValid`, `isDeleted`).
*   **Effects**: Pushed to the boundary (AppM / Effects layer).

### Elm (`docs/standards/languages/elm.md`)
*   **Boundaries**: Decoders MUST validate data. No raw JSON in Domain.
*   **State**: Use `RemoteData` pattern. No `isLoading` bools.
*   **Ports**: Envelopes required. No raw JS interop.

## 4. Operational Protocols
*   **Commits**: Conventional Commits (`type(scope): description`).
*   **PRs**: MUST include the "AI Verification Block" from `.github/pull_request_template.md`.
*   **Refactoring**: NEVER mix refactors with behavior changes.

## 5. Continuity Protocol
*   **Start of Session**: Read `docs/project_context.md` to sync with the "living memory" of the project.
*   **Anti-Trap**: Read `docs/playbooks/hallucinations.md` to avoid recurring AI-specific errors.
*   **End of Task**: Update `docs/project_context.md` with the new status, lessons learned, and next steps.

