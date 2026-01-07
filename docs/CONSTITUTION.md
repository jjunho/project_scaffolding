# Project Constitution v1

**(Authority · Precedence · Enforcement · AI-Aware Engineering)**

---

## 1. Purpose

This Constitution defines the **highest-level governing rules** of this project.

Its purpose is to:

* establish authority and precedence between documents,
* define what is mandatory vs advisory,
* define enforcement mechanisms,
* prevent drift, dilution, inconsistency, and unreviewable complexity,
* explicitly govern **AI-authored code** as a first-class concern.

All other documents derive their authority from this Constitution.

---

## 2. Normative Language

This project uses RFC-style keywords:

* **MUST** — mandatory; violation blocks merge or release
* **SHOULD** — strong recommendation; exceptions require justification
* **MAY** — optional

If a document does not use these terms, it is **non-normative**.

A rule that cannot be enforced **MUST NOT** be written as MUST.

---

## 3. Precedence Order (Law of Conflict)

If two rules conflict, the **higher-precedence document wins**.

Order of precedence:

1. **Project Constitution** (this document)
2. **Universal Project Standard**
3. **Process / CI / Release Standards**
4. **Architecture Standards**
5. **Domain / Frontend / Language Addenda**
6. **Security Policies**
7. **Examples, Recipes, and Templates**
8. **Tooling Docs, READMEs, Comments**

Lower-precedence documents **MUST NOT** weaken higher-precedence rules.

---

## 4. Enforcement Model

### 4.1 Merge and Release Gates

Rules marked **MUST** are enforced via:

* CI failures
* required checks
* branch protection
* review rejection

Passing CI is **necessary but not sufficient** for merge.

---

### 4.2 Single Gate Principle

Each project defines **one canonical quality gate** (e.g. `make check`).

* CI **MUST** call the gate
* CI **MUST NOT** re-encode its logic
* Local development **MUST** converge to CI behavior

---

## 5. Core Constitutional Principles

These principles apply **across all languages, tools, and layers**.

1. **Make illegal states unrepresentable**
2. **Explicit over implicit**
3. **Boundaries are correctness choke points**
4. **Separation of Concerns over convenience**
5. **Single source of truth**
6. **Determinism over cleverness**

All subordinate rules exist to enforce these principles.

---

## 6. AI-Aware Engineering (Mandatory)

This project is primarily authored by AI.
Therefore, AI-specific failure modes are treated as **systemic risks**, not user error.

### 6.1 AI Output Is Untrusted Input

* AI-generated code **MUST** be treated as untrusted until verified.
* “Looks correct” is not verification.

Verification **MUST** be provided by at least one of:

* deterministic tests,
* static analysis,
* compiler guarantees,
* a reproducible manual procedure.

---

### 6.2 Language Authority Rule (Non-Negotiable)

For languages with strong, explicit semantics (e.g. **Haskell**, **Elm**):

> **Official language documentation and compiler feedback override AI prior knowledge.**

If AI intuition conflicts with:

* the language specification,
* official documentation,
* or the compiler/type system,

then the AI intuition is wrong.

---

### 6.3 Mandatory Documentation Deference

AI **MUST** consult official language documentation when:

* a type error persists after one correction attempt,
* a solution “almost works” but feels unnatural,
* the implementation mirrors Java/Python/OOP patterns,
* the AI retries structurally similar solutions.

Retrying without changing assumptions is forbidden.

---

### 6.4 Assumption Reset Rule (Anti-Loop Guard)

If an AI-generated change:

* fails to compile,
* fails tests,
* or is rejected by the compiler

**more than once**, then the next attempt:

* **MUST** explicitly state which assumption was wrong,
* **MUST** replace it with a language-native concept.
* **MUST** reference or update the **Compiler Loop Playbook** (`docs/playbooks/compiler-loops.md`).

Without an assumption reset, further retries are disallowed.

---

### 6.5 Cross-Language Pattern Projection (Forbidden)

* **MUST NOT** project patterns from:

  * Java
  * Python
  * JavaScript OOP
  * Enterprise frameworks

…into languages like Haskell or Elm without explicit, documented justification.

Phrases such as:

* “This is how it’s usually done”
* “In most languages…”
* “A common approach is…”

are **merge-blocking red flags**.

---

### 6.6 Compiler Is Authority, Not Obstacle

* Compiler errors **MUST** be treated as guidance, not noise.
* Type errors **MUST** drive design changes.
* Errors **MUST NOT** be silenced or worked around to “make it compile”.

If the compiler disagrees, the design is wrong.

---

### 6.7 Anti-Complexity Rule (KISS, Enforced)

AI-authored code:

* **MUST** prefer the simplest correct solution.
* **MUST NOT** introduce:

  * speculative abstractions,
  * internal frameworks,
  * generic helpers without current necessity,
  * “utility dumping grounds”.

An abstraction is justified only if it removes existing duplication or enables a required capability **now**.

---

### 6.8 Locality and Change Containment (SoC)

AI-generated changes:

* **MUST** be narrowly scoped.
* **MUST NOT** mix refactors with behavior changes.
* **MUST** justify wide file changes explicitly.

Large blast radius without necessity is merge-blocking.

---

### 6.9 Dependency and Security Discipline (AI Risk Area)

* **MUST NOT** add dependencies casually.
* New dependencies **MUST** be:

  * justified,
  * version-pinned,
  * reputable.

Forbidden patterns include:

* `curl | sh`
* `eval`
* insecure temp file handling
* stringly-typed security decisions

---

### 6.10 Mandatory AI Verification Block

Any non-trivial AI-authored change **MUST** include:

* What changed (1–3 bullets)
* Why it is correct (tests/specs)
* How to verify locally (exact commands)
* Risk assessment
* Rollback plan (if applicable)

Missing this block is merge-blocking.

---

### 6.11 No Fabrication (The Honesty Rule)

* AI **MUST NOT** invent libraries, commands, files, or data that do not exist.
* If information is missing, the AI **MUST** explicitly state "I do not know" or "I need to verify this" rather than guessing.
* AI **MUST** verify the existence of imports, tools, and paths before using them.

"Hallucinating a solution" is a **breach of trust violation**.

---

## 7. Exceptions and Amendments

### 7.1 Exceptions

* Permanent exceptions **MUST** be documented in an ADR.
* Exceptions **MUST** be narrow and justified.
* Exceptions **MUST NOT** weaken this Constitution.

---

### 7.2 Amendments

* This Constitution **SHOULD** change rarely.
* Amendments require explicit review and justification.
* Changes must preserve conceptual integrity.

---

## 8. Non-Goals

This Constitution does not attempt to:

* prescribe specific vendors or frameworks,
* optimize prematurely for hypothetical scale,
* replace engineering judgment,
* accommodate convenience at the cost of correctness.

Evolution happens through addenda, not erosion of the core.

---

## Final Rule

If a change:

* weakens enforcement,
* blurs boundaries,
* duplicates logic across layers,
* increases complexity without necessity,
* or relies on AI intuition over language authority,

then it **violates this Constitution**, even if it “works”.

---

**End of Project Constitution v1**
