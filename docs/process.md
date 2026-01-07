# Process & Standards

> **Normative scope:** versioning, changelog, testing, observability, security, dependencies, code review, git discipline, general coding principles.

## Scope and Applicability

- **MUST** be enforced for all protected branches.
- **MUST NOT** be relaxed for tagged releases.

## Failure Taxonomy

Violations are classified by severity to guide review and remediation:

- **Invariant Violation**: Standard violation (formatting, linting errors, test failures). **NEVER ALLOWED** to merge.
- **Process Violation**: Procedural bypass (e.g., missing ADR for breaking change). **ALLOWED ONLY** with clear incident record.
- **Technical Debt**: Suboptimal pattern for tactical reason. **ALLOWED** with expiry date and documented rationale.

## Build & Quality Invariant

- **MUST**: The codebase builds successfully with zero warnings. A warning is treated as an error.
- **MUST**: All configured linters pass with no findings.
- **MUST**: Source code is fully formatted according to the project’s canonical formatters.
- **MUST NOT**: Any of the above be waived for protected branches or tagged releases.

## Versioning & Release (SemVer)

- **MUST**: The repository uses a unified version (SemVer `x.y.z`).
- **MUST**: Every release is documented in `CHANGELOG.md` following "Keep a Changelog" principles.
- **Release Flow**:
  1. Determine bump (MAJOR/MINOR/PATCH).
  2. Update `CHANGELOG.md`.
  3. Execute `make bump-version VERSION=x.y.z` (orchestrates updates across all components).
  4. Run `make check` (Validation gate).
  5. Commit: `chore(release): x.y.z`.
  6. Tag: `vX.Y.Z`.

## Test Policy

- **MUST**: Components implement automated tests covering happy paths and critical failure modes.
- **MUST**: Testing logic is encapsulated within each component.
- **Criteria**: New features require tests; bug fixes require regression tests.

## Observability

- **MUST**: Errors crossing component boundaries MUST be typed and loggable.
- **MUST**: Boundary failures MUST be observable via logs, metrics, or tracing.
- **MUST NOT**: Fail silently. All failures requires an observable trace.

## Security & Secrets

- **MUST**: No secrets in the repository. Use environment variables or secret managers.
**Definition of a "Clean Internal State"**:
- No uncommitted changes.
- No generated artifacts (ignored by git).
- No ignored-but-tracked files.

- **MUST**: Strict validation of boundaries/inputs at the entry point of every component.

## Git Discipline (The Highest Rule)

The repository MUST stay clean. Undisciplined history increases maintenance cost.

### 1. Logical Commits
- **MUST**: Single purpose per commit (feat, fix, refactor, docs).
- **MUST NOT**: Mix reformatting with functional changes.

### 2. Semantic Messages
Use **Conventional Commits**:
- `feat(scope): ...`
- `fix(scope): ...`
- `refactor(scope): ...`

### 3. Pre-commit Checklist
- [ ] `make status` to check detected components.
- [ ] `make check` passed (fmt, lint, test, build).
- [ ] `git diff` reviewed for accidental logic leaks or debug code.

## Git Hooks (Non-Negotiable Enforcement)

> Git hooks are mandatory local enforcement; CI is the final authority.

Git hooks are part of the repository’s control plane. They provide immediate local enforcement of the Build & Quality Invariant and prevent invalid commits from ever entering review. Hooks are mandatory.

### 1. Mandatory Installation and Presence

* **MUST**: This repository provides a canonical hook set under `scripts/git-hooks/`.
* **MUST**: Developers MUST configure git to use the repository hook path:
  * `git config core.hooksPath scripts/git-hooks`
* **MUST**: Tooling MUST provide an installer command (e.g., `make hooks`) that configures `core.hooksPath` correctly.
* **MUST**: CI MUST verify hook installation/configuration is present in the repo tooling (see “CI Enforcement” below).

### 2. Hook Contract (What Hooks Enforce)

Hooks MUST be fast, deterministic, and enforce standards locally.

* **MUST**: `pre-commit` enforces:
  * working tree sanity checks (no conflict markers, no accidental large/binary files unless allowlisted)
  * formatting and linting (or at minimum, verifies formatting/lint are clean)
  * optional targeted tests if fast; otherwise, defer full suite to `pre-push`
* **MUST**: `commit-msg` enforces:
  * Conventional Commits format (type/scope/message)
  * forbidden messages (“WIP”, “temp”, empty intent)
* **MUST**: `pre-push` enforces:
  * `make check` (or an equivalent full gate) before pushing to any branch intended for PR/merge

Hooks MUST fail closed: on violation they must block the operation.

### 3. Non-Bypass Policy (Exceptional Use Only)

Hook bypass is an exceptional procedure. It exists only to unblock urgent work when normal enforcement is temporarily impossible.

* **SHOULD NOT**: Use `--no-verify` to bypass hooks.
* **SHOULD NOT**: Disable hooks by altering `core.hooksPath`, deleting hook files, or using local overrides.
* **MUST**: Treat any bypass as a process incident that requires explicit justification and remediation.

#### Allowed Bypass Conditions (Narrowly Scoped)

Bypass is permitted only if ALL of the following are true:

* **MUST**: There is a concrete blocker preventing normal hook execution (e.g., hook tooling failure, corrupted local environment, urgent hotfix with verified CI path).
* **MUST**: The change is time-sensitive and delaying would cause material harm (incident response, production outage, security patch).
* **MUST**: The same enforcement will run in CI (or an equivalent trusted environment) before merge.

#### Bypass Procedure (Mandatory)

If bypass is used:

* **MUST**: Record the justification in the PR description (or incident ticket), including:
  * why hooks could not be run,
  * what risk is accepted temporarily,
  * the planned remediation step and timeline.
* **MUST**: Run the closest available gate immediately after (at minimum `make check`), in CI or locally once the blocker is resolved.
* **MUST**: Follow up with a remediation commit/PR if the bypass allowed any non-compliance to enter the branch.
* **MUST NOT**: Merge to protected branches unless CI is green and all invariants are satisfied.

#### Prohibited Uses (Never Acceptable)

* **MUST NOT**: Bypass for convenience, speed, or to avoid fixing failures.
* **MUST NOT**: Bypass to merge while red (failing build/lint/tests) except for the sole purpose of restoring green, with explicit approval per team policy.

### 4. CI and Server-Side Enforcement (Making It Truly Non-Negotiable)

Because local hooks can be bypassed, the repository MUST enforce the same rules centrally.

* **MUST**: CI status checks MUST run `make check` and block merges.
* **MUST**: CI MUST validate commit messages (Conventional Commits) for all commits in the PR, or at minimum the PR title if using squash-merge.
* **MUST**: CI MUST validate formatting is clean (no diff after `make fmt`) and lint is clean.
* **MUST**: Protected branches MUST reject direct pushes and require PRs with passing checks.

This makes hook bypass operationally pointless: even if someone bypasses locally, they cannot merge.

### 5. Standard Hook Entry Points (Single Source of Truth)

* **MUST**: Hooks MUST call Makefile targets (or scripts) rather than reimplementing logic.
* **MUST**: The root `Makefile` remains the canonical definition of `fmt/lint/test/build/check`.
* **MUST**: Hook scripts MUST be versioned in-repo and reviewed like any other code.

### 6. Performance and Developer Experience Requirements

* **MUST**: `pre-commit` MUST complete quickly (recommendation: seconds, not minutes) by using incremental checks when possible.
* **SHOULD**: `pre-push` may run the full suite and can take longer.
* **MUST**: Hook output MUST be actionable: clear failure reason and exact remediation command.

## How to Write Code

This section encompasses pre-coding preparation, continuous feedback obligations, and implementation principles.

### Agnostic Principles
- **Make Illegal States Unrepresentable**: Use the strongest type/schema system available in the chosen language.
- **Explicit over Implicit**: No hidden global states or magic side effects.
- **Clarity over Cleverness**: Readability is a technical requirement.

### Tooling & Workflow
- **Automation First**: MUST use canonical tooling for project scaffolding and repetitive boilerplate when such tooling exists.
    - Haskell: `stack init` (lots of possibilities of settings).
    - Elm: `elm init`, `elm-land init`.
- **Feedback Loop**: Compiler warnings, hints, and tooling suggestions are actionable signals. They MUST be addressed; warnings are not ignorable unless explicitly justified.
- **Build Awareness**: Coding against a broken or unknown build state is prohibited.

---

## Automation Contract (Makefile)

The root `Makefile` is the source of truth for project-wide standards. It enforces:

- `make fmt`: Format source code.
- `make lint`: Run static analysis.
- `make test`: Execute test suites.
- `make build`: Verify buildability/artifacts.
- `make check`: The canonical quality gate (`fmt + lint + test + build`).

These commands MUST enforce the **Build & Quality Invariant** (e.g., warnings as errors).
