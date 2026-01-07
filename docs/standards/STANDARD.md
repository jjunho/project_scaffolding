# Universal Project Standard — Core (v1.0)

> **This document is normative and predominantly language-agnostic.**
> It defines the **minimum acceptable standard** for professional software projects.
> Language-, framework-, or domain-specific rules **MUST** be defined in separate addenda and **MUST NOT** contradict this standard.

---

## RFC-style keywords

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as described in RFC 2119.

* **MUST** – mandatory; violation blocks merge or release.
* **SHOULD** – strong recommendation; deviations require explicit justification.
* **MAY** – optional.

---

## Scope and applicability

* This standard **MUST** apply to:

  * Protected branches (e.g. `main`, `release/*`)
  * Release builds and versioned artifacts
* This standard **MAY** be relaxed:

  * On non-protected experimental branches
  * Only with explicit documentation of scope and intent
* This standard **MUST NOT** be relaxed:

  * For releases
  * For production code
* Enforcement **MUST** be implemented via:

  * Mandatory CI (format, lint, test, build when applicable)
  * Branch protection rules
  * Required approvals
  * Any bypass **MUST** be documented via an ADR or incident record

---

## Core principles (universal)

### 1. Make illegal states unrepresentable

Systems **MUST** be designed such that invalid states cannot exist.

* Invariants **MUST** be enforced through:

  * Types
  * Schemas
  * Contracts
  * Boundary validation
* Strict preference order:

  1. Compile-time guarantees
  2. Runtime validation
  3. Documentation (last resort)

---

### 2. Explicit over implicit

Nothing relevant may be hidden.

* Effects, errors, and dependencies **MUST** be explicit
* Implicit global state is **PROHIBITED**
* Silent failures are **PROHIBITED**
* Dependencies **MUST** be declared and injected through explicit contracts

---

### 3. Clarity over cleverness

Readability is a technical requirement.

* Abstractions **MUST** reduce cognitive load
* Code that requires guesswork violates this standard
* If comments are required to explain obvious behavior, the design is incorrect

---

### 4. Correctness before optimization

* Correct behavior is non-negotiable
* Performance work **MUST** be:

  * Hypothesis-driven
  * Measured
  * Documented
* Premature optimization is technical debt

---

## Non-negotiable heuristics

* **DRY** – every change must have a single source of truth
* **KISS** – complexity requires justification
* **YAGNI** – no functionality outside the current release scope
* **Separation of Concerns (SoC)** – clear boundaries between:

  * Orchestration
  * Domain logic
  * Infrastructure

Violations **MUST** be documented via ADR, including a concrete plan for removal.

---

## Project organization

### Required conceptual structure

```
.
├── README.md
├── CHANGELOG.md
├── .gitignore
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── setup.md
│   └── adrs/
├── src/
├── test/
├── scripts/
├── ci/
└── automation-entrypoint
```

### Automation entrypoint (language-agnostic)

Projects **MUST** provide a single, documented automation entrypoint, such as:

* Makefile
* npm / yarn scripts
* gradle / maven
* dotnet CLI
* pyproject.toml / setup.py
* Workspace scripts (APL/J/K)

The chosen mechanism **MUST** be documented in `README.md`.
The automation entrypoint **MUST** expose human-invocable commands and be discoverable without reading source code.

---

## Documentation requirements

* `README.md` **MUST** describe:

  * Project purpose
  * Build instructions
  * Test execution
  * Runtime usage
* `docs/README.md` **MUST** index all documentation
* Significant decisions **SHOULD** be documented via ADRs
* Stale documentation is technical debt

---

## Versioning and release

### Versioning policy (mandatory, documented choice)

Each project **MUST** adopt exactly one consistent versioning scheme:

* **Public libraries:** Semantic Versioning (SemVer) is mandatory
* **Applications/services:** SemVer or Calendar Versioning (YYYY.MM.MICRO)
* **Internal tools:** Simplified SemVer (MAJOR.MINOR)
* **Schemas/contracts:** Independent schema versioning (v1, v2, …)

The chosen scheme **MUST** be stated explicitly in the header of `CHANGELOG.md`.

---

### Release constraints

* A single authoritative version per repository
* Releases **MUST** be:

  * Automated
  * Deterministic
  * Originated from protected branches only
* Green CI is a hard prerequisite

---

## Quality baseline

### Owned code

* Compiler/interpreter warnings **MUST** be zero **OR** explicitly suppressed
* Suppressions **MUST** follow this format:

```
SUPPRESS(warning-id): <ticket> <reason>
Expected resolution: <date|version>
```

### Dependencies

* Dependency warnings **MAY** be tolerated only if:

  * They do not indicate unsafe behavior
  * Upgrading would break compatibility
  * They are actively tracked

---

## Testing contract

### Minimum coverage (when applicable)

* Business logic: ≥80%
* Utilities/helpers: ≥90%
* UI / glue code: ≥60%
* Generated code: MAY be excluded
* Coverage requirements **MAY** be waived for components where coverage is not a meaningful signal, provided the rationale is documented via ADR.

### Required test types

* **Unit tests:** pure logic and transformations
* **Integration tests:** I/O boundaries (DB, filesystem, network)
* **Property-based tests:** parsers, codecs, validators
* **End-to-end tests:** top 3–5 critical user flows

### Mandatory failure cases

* Invalid input
* Boundary conditions (empty, null, max size)
* Infrastructure failures (timeouts, external dependency errors)

Flaky tests are unacceptable.

---

## Git hygiene and workflow

Each project **MUST** document its chosen workflow.

### Accepted strategies

**Trunk-based development (recommended):**

* Feature branches live ≤2 days
* Merge via squash
* `main` is always deployable

**GitHub Flow:**

* Feature branches off `main`
* Consistent merge strategy (squash OR merge commits)

**Git Flow:**

* `main` = production
* `develop` = staging

Rebase rules:

* Allowed only on local or feature branches
* Prohibited on shared or protected branches

---

## Error handling (non-dogmatic)

Error handling **MUST** follow language-idiomatic conventions consistently:

* **Errors as values:** Go, Rust, Haskell, OCaml
* **Exceptions:** Java, C#, Python
* **Hybrid:** JavaScript / TypeScript
* **Sentinel values / flags:** C, APL (must be documented)

Silencing errors without logging is **PROHIBITED**.

---

## Build automation contract

Projects **MUST** expose the following targets:

### Always required

* `check` – full quality gate (fail fast)
* `test`
* `clean`

### When applicable

* `fmt`
* `lint`
* `build`
* `install`
* `release`

Monorepos **MUST** provide scoped targets (e.g. `test:api`, `test:all`).

---

## Dependency management

* A lockfile **MUST** exist
* Exact versions **MUST** be used in production
* Update process **MUST** be documented
* Large or invasive dependencies **MUST** be justified via ADR

---

## Security baseline

* Secrets in the repository are **PROHIBITED**
* Secret scanning **MUST** run (pre-commit or CI)
* Vulnerability scanning **MUST** run in CI
* High/critical vulnerabilities **MUST** be addressed within 7 days
* Input **MUST** be validated at boundaries
* Sensitive data **MUST NOT** be logged without masking

---

## Observability (when applicable)

* Structured logging (JSON or logfmt)
* When observability applies, cevels: DEBUG, INFO, WARN, ERROR
* Correlation IDs are mandatory
* Metrics: RED or USE methodology
* Tracing via W3C Trace Context

Libraries and offline tools may mark observability as N/A with justification.

---

## Accessibility (UI projects)

* WCAG 2.1 Level AA minimum
* Keyboard navigability required
* Adequate contrast ratios
* Semantic HTML and correct ARIA usage

---

## Disaster recovery (when applicable)

* Tested backups
* Rollback capability within 5 minutes
* Reversible database migrations
* Blameless postmortems required after incidents

---

## Exceptions process

Any exception to a **MUST** or **SHOULD** **MUST** document:

* Rationale
* Scope
* Expiry date or condition

Undocumented exceptions are defects.

---

## Adoption roadmap

**Phase 1 (immediate):**

* Structure
* README
* Basic CI

**Phase 2 (30 days):**

* Formatter enforcement
* Linter
* ADRs
* Coverage measurement

**Phase 3 (90 days):**

* Security scanning
* Zero warnings
* Observability
* Disaster recovery

---

## Compliance levels

* **Level 1:** structure + CI + tests
* **Level 2:** + documentation + security + observability
* **Level 3:** + disaster recovery + SLOs + incident response
Projects **SHOULD** explicitly declare their current compliance level in `README.md`.


---

## Final rule

If the code:

* allows invalid states,
* hides effects or failures,
* lacks meaningful tests,
* relies on comments to explain obvious behavior,
* or requires guesswork to understand,

then it **DOES NOT MEET THIS STANDARD**, regardless of whether it works.

---

**This document defines the minimum acceptable standard for professional software engineering.**
