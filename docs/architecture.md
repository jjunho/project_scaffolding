# Architecture & Project Organization

> **Normative scope:** project structure, documentation requirements, migrations, CI/CD, quality baseline (zero warnings/errors required for merge).

## Principles of Agnostic Scaffolding

This project uses a delegation-based architecture. The root repository orchestrates high-level goals, while specific implementation details (language, framework, build tool) are encapsulated within component directories.

Each component directory **MUST** expose the standard targets (`fmt`, `lint`, `test`, `build`, `check`) and **MUST NOT** require the root to know tool-specific commands.

## Scope and Applicability

- **MUST** apply to all code merged to protected branches (e.g., `main`).
- **MAY** be relaxed on non-protected branches for experiments.
- **MUST NOT** be relaxed for releases/tagged builds.

## Merge Blocking

- **MUST**: `build` fails on warnings (warnings treated as errors or equivalent strict mode).
- **MUST**: `lint` fails on any violation unless explicitly allowlisted.
- **MUST**: `fmt` is idempotent and produces no diff.
- **MUST**: CI status checks block the merge; branch protections enforce this.
- Reviews require approval according to team policy.
- Exceptional bypasses MUST be documented in an ADR.

## Organization

- **src/**: Contains primary project components (services, apps, libraries).
- **shared/**: Agnostic logic, types, or protocols shared between components.
    - **MUST**: Contains only versioned, dependency-disciplined, reusable modules with explicit owners.
    - **MUST NOT**: Import "shared" by path hacks; consume it as a proper package/module where the ecosystem supports it.
    - Changes to `shared/` **MUST** be treated as potentially breaking and require explicit review.
- **docs/**: Living documentation, architecture standards, and ADRs.
- **scripts/**: Agnostic automation (SemVer, Changelog, CI helpers).
- **ci/**: CI configuration.
    - **MUST**: Invoke `make check` (root and/or per-component) as the canonical gate.
    - **MUST**: Fail if `make check` produces warnings, even if exit code is zero.
    - **MAY**: Add environment setup and caching, but **MUST NOT** re-encode the quality logic in bespoke steps.

### Dependency Direction

- Components **MAY** depend on `shared/`.
- Components **MUST NOT** depend on each other directly to maintain encapsulation.
- Root orchestration **MUST NOT** import component internals.
- Cycles between components are **FORBIDDEN**.

### Component Lifecycle

Components in `src/` fall into one of three statuses:

- **Experimental**: May have relaxed rules (documented in `README`), no breaking change guarantees.
- **Internal**: Fully compliant but API may change without version bump; for internal use only.
- **Stable**: Fully compliant, public API changes require a formal migration path.

### Generic Skeleton

```
.
├── Makefile             # Agnostic orchestration
├── CHANGELOG.md         # Unified release history
├── README.md            # Project entry point
├── docs/                # Standards and ADRs
├── scripts/             # Universal automation
├── src/
│   ├── component-a/     # Encapsulated implementation (Haskell, Elm, etc.)
│   │   ├── Makefile     # Component contract (fmt, lint, test, build, check)
│   │   └── src/
│   └── component-b/
└── ci/                  # CI/CD pipelines
```

## Documentation Requirements

- **MUST**: `README.md` at repo root → Purpose, Quick Start, Automation layout.
- **SHOULD**: `docs/README.md` (index to all other standards).
- **SHOULD**: Each component has a `README.md` documenting purpose, local dev commands, and any non-obvious dependencies.
- **MUST**: Each major architectural decision documented as an **ADR** in `docs/adrs/`.

## Quality Baseline

- **MUST**: Zero compiler warnings in strict mode.
- **MUST**: Formatting enforced by automated tools.
- **MUST**: Linters must pass with zero violations.
    - Exceptions **MUST** be recorded in-repo (e.g., `docs/exceptions/` or local `lint.allowlist`), include rationale, scope, and expiry/owner.
- CI enforces these; local `make check` provides the same guarantee.

## Versioning Boundary

- The repository **MUST** have a single release version marked by a git tag (e.g., `v1.2.3`).
- Components **MUST NOT** define independent public release versions.
- All internal component manifests **MUST** synchronize with this version during the release process via `make bump-version`.

## Migration Policy

Breaking changes in `shared/` or stable components require:

- **ADR**: A documented decision record explaining the change.
- **Changelog**: Explicit entry in `CHANGELOG.md` under "BREAKING CHANGES".
- **Version Bump**: A MAJOR version increment.
- **Compatibility Shims**: **SHOULD** be provided where possible for one release cycle to ease transition.

