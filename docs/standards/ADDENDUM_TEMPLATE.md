# Language Addendum Template

> Use this template to create a language-specific addendum for a new language.
> Copy this file, rename it to `docs/standards/LANGUAGE.md`, and fill in the sections below.
> **All addenda MUST extend (never contradict) the Universal Project Standard.**

---

## [Language] Language Addendum

> **This document extends the Universal Project Standard for [Language] projects.**
> All universal rules apply unless explicitly refined here.

---

## Scope

Applies to:

* [List project types: e.g., Node.js services, CLI tools, libraries, etc.]
* [Framework/runtime baseline: e.g., Node.js 18+ LTS, Python 3.10+, etc.]

If a rule is N/A (e.g., observability for a small utility), it **MUST** be documented as such, with rationale.

---

## Language-specific core principles

### 1. [First principle]

**Define the primary design philosophy for this language.**

### 2. [Second principle]

**Define enforcement mechanisms specific to this language.**

### 3. [Third principle]

**Define error/boundary handling specific to this language.**

---

## Project structure (recommended)

```
.
├── Makefile (or equivalent: package.json, Cargo.toml, etc.)
├── README.md
├── CHANGELOG.md
├── src/
├── test/
├── docs/
├── scripts/
└── ci/
```

**Rules:**

* **MUST**: [first structural requirement]
* **MUST**: [second structural requirement]
* **SHOULD**: [optional structural recommendation]

---

## Formatting, linting, and static analysis

**Mandatory tools:**

* Formatter: [specify tool, e.g., black, prettier, rustfmt]
* Linter: [specify tool, e.g., ruff, eslint, clippy]
* Type checker: [specify tool, e.g., mypy, tsc, if applicable]

**Rules:**

* **MUST** apply formatting automatically.
* **MUST** treat lint violations as CI failures.
* **MUST** not disable rules globally to "make CI green".

---

## Testing

* **MUST** use [primary test framework: e.g., pytest, jest, vitest].
* **MUST** keep tests deterministic.
* **MUST** [language-specific test requirement].

---

## [Key domain: e.g., "Error handling", "Async/concurrency", "Package management"]

**Define the most critical operational rule for this language.**

* **MUST**: [rule 1]
* **MUST**: [rule 2]
* **SHOULD**: [recommendation]

---

## Build and automation contract

Projects **MUST** provide equivalents of:

* `fmt` → [formatter command]
* `lint` → [linter command]
* `test` → [test command]
* `build` → [build command]
* `check` → sequential: fmt && lint && test && build
* `precommit` → check + clean working tree guard

---

## Forbidden anti-patterns

* [Anti-pattern 1 specific to this language]
* [Anti-pattern 2 specific to this language]
* [Anti-pattern 3 specific to this language]

---

## Final rule

If the code:

* [violation 1],
* [violation 2],
* [violation 3],
* or [violation 4],

then it **violates this standard**, even if it [language-specific caveat].

---

## Guidance for authors

When creating an addendum for a new language:

1. **Start with universals**: Review [STANDARD.md](STANDARD.md) and adopt all rules that apply.
2. **Identify gaps**: What does the universal standard not address that this language requires?
3. **Define one core principle**: What is the language's strongest feature or biggest risk? Make that explicit.
4. **Specify tools**: Name exact tools (formatter, linter, type checker). No vagueness.
5. **Layer the project**: Define module/package structure that makes violations visible.
6. **Make violations enforceable**: If you can't detect it in CI or code review, don't add it.
7. **Forbid anti-patterns explicitly**: List the patterns you've seen fail in practice.
8. **Keep it short**: If your addendum is longer than 2 pages, you're probably over-specifying. Consolidate.

---

## Template checklist

Before committing your addendum:

- [ ] Title is clear: "[Language] Language Addendum"
- [ ] Scope section specifies language version baseline
- [ ] At least 1 core principle defined (and mandatory)
- [ ] Project structure with clear layering rules
- [ ] Formatting/linting/testing tools named explicitly
- [ ] Build automation contract includes all canonical targets
- [ ] Forbidden anti-patterns section exists and is specific
- [ ] Final rule is enforceable (not aspirational)
- [ ] No contradictions to Universal Standard
- [ ] Document does not exceed 4 pages (edit ruthlessly)
- [ ] Link from [docs/standards/README.md](README.md) added

---

**This template exists so new language addenda are consistent, enforceable, and maintainable.**
