# Makefile Addendum

**(Single Entry Point, Deterministic Gates, Human-Readable UX)**

> This document extends the Universal Project Standard for repositories that use `make` as the canonical developer/CI entrypoint.
> The Makefile is treated as an **automation boundary**: it orchestrates tools; it must not become a second build system.
> All universal rules apply unless explicitly refined here.

---

## Scope

Applies to:

* Root `Makefile` and any included `.mk` files
* Developer workflows (`make fmt`, `make lint`, `make test`, `make build`, `make check`)
* CI scripts that invoke `make`

Non-goals:

* Encoding complex build graphs better handled by the language build tool (Stack/Cabal, npm/pnpm, etc.)
* Implementing business logic

---

## 1. Fundamental Rule (Non-Negotiable)

> `make` **MUST** be the single stable interface for common actions, and **MUST** be consistent between local and CI.

The Makefile’s purpose is:

* to provide a small set of stable targets
* to enforce a deterministic “quality gate”
* to hide tool invocation details without hiding failures

If a developer must remember bespoke commands instead of using `make`, the Makefile failed.

---

## 2. Canonical Targets (Mandatory)

The repository **MUST** provide these targets at the root:

* `make help` (or default target) — prints help
* `make status` — prints repo + tooling status
* `make fmt` — formatting only
* `make lint` — linting/static analysis only
* `make test` — test suite only
* `make build` — compilation/build artifacts only
* `make check` — full gate: `fmt + lint + test + build`
* `make clean` — remove build artifacts safely

Rules:

* `make` (no args) **MUST** display help or run `make help`.
* Targets **MUST** be idempotent.
* Targets **MUST** fail on errors; success must mean “clean pass”.

---

## 3. The Gate Contract (Merge-Blocking)

### 3.1 `check` is the single quality gate

* `make check` **MUST** be the canonical gate used by CI.
* CI **MUST NOT** re-encode the gate logic in YAML (CI calls `make check`).
* If CI needs extra steps (cache restore, service setup), they occur outside the gate; the gate remains identical.

### 3.2 Clean repository invariant

* `make check` (or `make precommit`, if present) **MUST** fail if the working tree is dirty when the project requires a clean tree for release/commit discipline.
* Generated artifacts must be either:

  * fully reproducible and committed intentionally, or
  * in `.gitignore` and not produced in a way that dirties the tree unintentionally.

---

## 4. UX Requirements (Help and Output)

### 4.1 Help is mandatory and standardized

* A help target **MUST** exist.
* Help output **MUST** list:

  * target name
  * short description
  * (optional) important variables

Help output **MUST** be stable and readable in 80–120 columns.

### 4.2 Output discipline

* Commands invoked by Make **MUST** print meaningful progress.
* Failure output **MUST** surface the failing command and log context.
* The Makefile **MUST NOT** silence failures via `-` prefixes or `|| true`.

Recommended:

* Use `@` sparingly (only to reduce noise, not to hide commands).
* Prefer explicit echo lines for major phases.

---

## 5. Determinism and Portability

### 5.1 Shell and safety

* The Makefile **MUST** specify a shell explicitly:

  * `SHELL := /usr/bin/env bash` (recommended)

* Recipes **SHOULD** use shell strict mode when multi-line:

  * `set -euo pipefail; ...`

Avoid bash-specific features if your shell is not bash.

### 5.2 Tooling versions and environment

* Tool versions **SHOULD** be pinned where feasible (lockfiles, toolchain config).
* Make targets **MUST** not depend on interactive prompts.
* Targets **MUST** be deterministic given the same inputs.

### 5.3 Variables and configurability

* Targets **MAY** accept variables (e.g., `VERSION=x.y.z`), but:

  * variables must have documented defaults
  * invalid values must fail fast with clear errors

---

## 6. Structure and Maintainability

### 6.1 Split when necessary, but keep a single entrypoint

If the Makefile grows:

* **MAY** split into `make/*.mk` or `mk/*.mk` files
* Root `Makefile` **MUST** remain the entrypoint and include them
* Includes **MUST** not change target semantics silently

### 6.2 No “utils dumping ground”

* Helper logic belongs near the target it serves.
* Reusable shell logic belongs in `scripts/` as a real script (then Make calls it).

Rule of thumb:

* If a recipe exceeds ~10–15 lines, extract to a script.

---

## 7. Anti-Patterns (Merge-Blocking)

* CI calling ad-hoc commands instead of `make check`
* “God targets” that do everything with no separation (`make all`)
* Non-idempotent targets (second run changes behavior)
* Silencing failures (`-cmd`, `|| true`) without explicit rationale
* Interactive prompts inside targets
* Tool installation inside `make` (install belongs to setup scripts/docs)
* Complex build logic duplicating language build tools

---

## Reviewer Checklist (Merge-Blocking)

A Makefile change is approvable only if:

1. `make check` exists and remains the CI gate.
2. Targets are composable: `fmt`, `lint`, `test`, `build` are separate and deterministic.
3. Output is human-readable; failures are not masked.
4. Shell is explicit; recipes are safe and portable for the repo’s target environment.
5. Any new variables are documented and validated.
6. Large recipes are factored into scripts.

---

## Appendix — Recommended help format

A compact, column-aligned style is preferred:

```
Targets:
  help           Show this help.
  status         Show repo status and tool versions.
  fmt            Format all code.
  lint           Run linters (no formatting).
  test           Run tests.
  build          Build/compile.
  check          Gate: fmt + lint + test + build.
  clean          Remove build artifacts.

Variables:
  VERSION=x.y.z  Release version used by changelog/tag steps.
```

---

## Final Rule

If `make`:

* hides failures,
* diverges between local and CI,
* or becomes a parallel build system,

then it **violates this standard**, even if it “works.”
