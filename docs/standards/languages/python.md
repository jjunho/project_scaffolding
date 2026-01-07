# Python Language Addendum

> **This document extends the Universal Project Standard for Python projects.**
> All universal rules apply unless explicitly refined here.

---

## Scope

This addendum applies to:

* Python applications, services, libraries, CLIs, and automation
* CPython ≥ 3.10 (earlier versions require explicit justification)

If a rule is not applicable (e.g., observability for a small library), it **MUST** be documented as N/A with rationale.

---

## Python-specific core principles

### 1. Explicit is enforced, not optional

Python allows implicit behavior; this standard forbids relying on it.

* **MUST** avoid implicit globals, monkey-patching, or dynamic attribute injection.
* **MUST** avoid runtime magic that alters behavior invisibly (`__getattr__`, `__setattr__`, import-time side effects) unless strictly necessary and documented.
* **MUST** prefer explicit data flow over introspection.

---

### 2. Types are mandatory at module boundaries

Python is dynamically typed; correctness must be recovered via typing.

* **MUST** use type hints (`typing`) for:

  * Public APIs
  * Function/method parameters and return values
  * Dataclass fields
* **SHOULD** type all internal functions unless trivial.
* **MUST** run a type checker (`mypy`, `pyright`, or equivalent) in CI.
* **MUST** not silence type errors globally; local ignores require justification.

**Guiding rule:**

> "Untyped public code is undocumented behavior."

---

### 3. Errors are values, not side effects

* **MUST** not use exceptions for normal control flow.
* **MUST** define and raise domain-specific exceptions where errors are exceptional.
* **MUST** catch exceptions at system boundaries only.
* **MUST** never swallow exceptions silently.
* **SHOULD** use `Result`-like patterns (explicit return objects) where error handling is part of normal logic.

---

## Project structure (Python)

A canonical Python project **MUST** follow one of the approved layouts:

### Application / Service

```
.
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       └── ...
├── tests/
├── docs/
├── scripts/
└── ci/
```

### Library

```
.
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── src/
│   └── package_name/
├── tests/
├── docs/
└── ci/
```

* **MUST** use `src/` layout to avoid import ambiguity.
* **MUST NOT** rely on implicit working-directory imports.

---

## Dependency and environment management

* **MUST** use `pyproject.toml` (PEP 518/621).
* **MUST** pin direct dependencies with compatible ranges.
* **SHOULD** lock transitive dependencies (`poetry.lock`, `uv.lock`, `requirements.lock`).
* **MUST NOT** rely on system Python without isolation.

### Environments

* **MUST** use virtual environments.
* **MUST** document Python version and environment setup.
* **SHOULD** provide `make venv` or equivalent automation.

---

## Formatting, linting, and static analysis

### Mandatory tools (or equivalents)

* Formatter: **black**
* Import sorting: **isort**
* Linting: **ruff** (preferred) or `flake8` + plugins
* Typing: **mypy** or **pyright**

### Rules

* **MUST** apply formatting automatically.
* **MUST** treat lint violations as CI failures.
* **SHOULD** enable strict typing mode incrementally.
* **MUST NOT** disable rules globally to "make CI green".

---

## Code style and idioms

### Functions and modules

* **MUST** keep functions small and single-purpose.
* **SHOULD** avoid deep nesting; refactor into helpers.
* **MUST** avoid large "utility" modules.

### Data modeling

* **MUST** use:

  * `dataclasses` or `attrs` for structured data
  * `Enum` for closed sets
* **MUST NOT** use bare dictionaries as domain models beyond boundaries.
* **SHOULD** validate data at boundaries (e.g., `pydantic`, `attrs` validators).

---

## Imports

* **MUST** use absolute imports within the project.
* **MUST** avoid circular imports; refactor instead.
* **SHOULD** group imports: stdlib → third-party → local.
* **MUST NOT** use wildcard imports (`from x import *`).

---

## Testing (Python-specific)

* **MUST** use `pytest`.
* **MUST** isolate tests; no reliance on execution order.
* **MUST** avoid shared mutable global state in tests.
* **SHOULD** use fixtures for setup/teardown.
* **SHOULD** use property-based testing (`hypothesis`) for invariants.

### Anti-patterns

* Sleeping to "wait" for async behavior.
* Tests depending on network unless explicitly integration tests.
* Mocking internal implementation instead of behavior.

---

## Performance and correctness

* **MUST** measure before optimizing.
* **MUST** document performance-sensitive paths.
* **SHOULD** prefer algorithmic improvements over micro-optimizations.
* **MUST NOT** sacrifice clarity for unmeasured speed.

---

## Concurrency and async

* **MUST** clearly separate sync and async code.
* **MUST NOT** mix blocking I/O in async paths.
* **SHOULD** prefer structured concurrency patterns.
* **MUST** document concurrency assumptions and invariants.

---

## Security (Python-specific)

* **MUST** avoid `eval`, `exec`, and dynamic code execution unless strictly necessary and documented.
* **MUST** validate external input aggressively.
* **MUST** pin dependencies with known security posture.
* **SHOULD** run dependency vulnerability scans.

---

## Build and automation targets (Python)

Python projects **MUST** expose equivalents of:

* `fmt` → black + isort
* `lint` → ruff / flake8
* `typecheck` → mypy / pyright
* `test` → pytest
* `build` → package build / app build
* `check` → fmt + lint + typecheck + test + build

---

## Anti-patterns explicitly forbidden

* "Just Python" scripts without structure for non-trivial projects
* Hidden runtime mutation
* Silent exception handling
* Untyped public APIs
* Global state as configuration
* Mixing formatting, refactors, and behavior in one commit

---

## Final Python rule

If Python code:

* relies on implicit behavior,
* lacks type annotations at boundaries,
* hides errors in exceptions,
* uses dictionaries as domain models,
* or requires execution to understand intent,

then it **violates this standard**, even if it passes tests.

---

**This addendum exists to compensate for Python's flexibility with discipline.**
