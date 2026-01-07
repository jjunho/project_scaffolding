# Project Active Context

> **PURPOSE**: This is the "living memory" of the project. AI agents MUST read this at the start of every session and update it after every significant change to maintain continuity.

## 1. Current High-Level Status
- **Phase**: Infrastructure Hardening & AI Setup.
- **Last Milestone**: Completed "AI-Defensive" scaffolding (Hooks, Linters, Architecture checks).
- **Next Milestone**: Initialize core components in `src/backend` (Haskell) and `src/frontend` (Elm).

## 2. Active Focus & Workstreams
- **Hardening (Current)**: Finalizing the "Memory Bank" and long-term continuity protocols.
- **Architecture**: Enforcing pure domain kernels via `scripts/check_architecture.py`.
- **Safety**: Monitoring `docs/playbooks/hallucinations.md` for tool-usage regressions.

## 3. Recent Decisions & Lessons
- **Decision**: Adopted a root `pyproject.toml` for strict typing in automation scripts.
- **Lesson**: Standard git hooks path (`.git/hooks`) is not committed; using `scripts/git-hooks` + `git config core.hooksPath` is the only way to enforce AI discipline locally.
- **Lesson**: AI context windows are fragile; `docs/AI_README.md` is the primary anchor for machine reasoning.

## 4. Immediate Next Steps
- [ ] Initialize Haskell project skeleton in `src/backend`.
- [ ] Initialize Elm Land project in `src/frontend`.
- [ ] Verify `make check` propagates correctly to sub-modules.

## 5. Active Constraints
- **NO SEMI-PURE DOMAIN**: Do not allow `IO` or `Http` to leak into `src/Domain` files.
- **STRICT COMMITS**: Conventional commits only.
- **NO PRINT**: Use structured logging or tracers.
