# Haskell (RIO) Language Addendum

**(ReaderT/RIO as the Effect Boundary, Safe Prelude, Qualified Imports, Deterministic Logging)**

> This document extends the Project Constitution v1 and the Universal Project Standard for Haskell codebases that adopt **rio** as the standard library.
> It is normative. All “MUST/SHOULD/MAY” rules are enforceable expectations for merge/release.

## Scope

Applies to:

* All Haskell application code in this repository (executables, services, workers, CLIs).
* Shared library code in-repo when the project standardizes on RIO.
* Logging, process execution, exception handling, and IO boundaries.

Non-goals:

* Teaching Haskell fundamentals.
* Supporting multiple incompatible prelude stacks simultaneously.

---

## 1. Fundamental Rule

> The default effect model of this project is **RIO env a** (ReaderT env IO a).
> We treat the environment and boundaries as correctness choke points.

If a design fights this model, the design is wrong.

---

## 2. Prelude and Imports

### 2.1 NoImplicitPrelude + RIO prelude (mandatory)

* Modules **MUST** use `{-# LANGUAGE NoImplicitPrelude #-}` and `import RIO` as the default.
* Exceptions require explicit justification (e.g., minimal boot files, unusual tooling modules).

Rationale: avoids common base pitfalls (partial functions, unsafe defaults) and normalizes the project’s vocabulary.

### 2.2 Qualified imports for common types (mandatory)

* Text/bytestring/containers modules **MUST** be imported qualified via the `RIO.*` modules using canonical short aliases.

Examples:

* `import qualified RIO.Text as T`
* `import qualified RIO.ByteString as B`
* `import qualified RIO.Map as Map`
* `import qualified RIO.Set as Set`

Rules:

* **MUST NOT** add dependencies solely to import “convenience” variants when RIO already reexports safe APIs.
* **MUST** keep imports consistent across modules to reduce cognitive load and AI drift.

---

## 3. The Default Monad: RIO

### 3.1 Application code uses RIO by default (mandatory)

* Application logic **MUST** be written in `RIO env` unless there is a clear reason to generalize.
* Generalization to `(MonadReader env m, MonadIO m, …)` **MAY** be used for reusable library functions, but **SHOULD** be avoided in application modules due to worse error messages and slower iteration.

### 3.2 Effects and purity boundaries

* Domain logic **SHOULD** remain pure and be called from RIO boundary modules.
* IO and side effects **MUST** be localized to boundary layers (startup, persistence, network, filesystem, process execution).

---

## 4. Environment Design

### 4.1 Environment is explicit and minimal (mandatory)

* The environment `env` **MUST** contain only cross-cutting services/config needed broadly.
* The environment **MUST NOT** become a dumping ground for arbitrary values.

Guideline: if a value is used by a single function chain, pass it explicitly; do not promote it into `env`.

### 4.2 Has* typeclasses (mandatory for libraries / shared components)

When code is intended to be reused across environments:

* Shared functions **MUST** depend on `Has*` capabilities rather than concrete `App` types.

Example pattern:

* `HasLogFunc env`
* `HasProcessContext env`
* project-specific: `HasDb env`, `HasHttpClient env`, etc.

---

## 5. Lenses policy for Has* capabilities

RIO encourages lenses for “get + set” environment access.

Rules:

* If a capability needs only read access, a getter-style `Has*` **MAY** be acceptable.
* If code needs to *modify* a capability via `local`, then the `Has*` typeclass **MUST** expose a `Lens' env X`.

Preferred idiom:

* Read: `view handleL`
* Scoped override: `local (set handleL newHandle) action`

AI-specific guardrail:

* **MUST NOT** introduce Template Haskell or generics automation just to avoid lens boilerplate. The boilerplate is intentionally “safe” and reviewable.

---

## 6. Logging (mandatory)

### 6.1 No ad-hoc stdout printing

* Application output **MUST** use RIO logging (`logInfo`, `logWarn`, `logError`, `logDebug`) rather than `putStrLn`, except for deliberate user-facing CLI output where logging is not appropriate.
* User-targeted vs machine-targeted output **MUST** be explicitly distinguished.

### 6.2 Logging capability

* Any environment used with logging **MUST** provide `HasLogFunc env`.
* `runSimpleApp` **MAY** be used for trivial scripts/prototypes, but production entrypoints **SHOULD** construct `LogOptions` and `LogFunc` explicitly.

### 6.3 Builder types, not String

* Log messages **MUST NOT** rely on `String` concatenation by default.
* Use `Utf8Builder` patterns (`<>`, builders) and `OverloadedStrings` where appropriate.

---

## 7. External processes (mandatory when applicable)

* External process execution **MUST** use `RIO.Process` / typed-process patterns rather than shelling out via ad-hoc `System.Process` calls.
* Environments that run processes **MUST** provide `HasProcessContext env`.
* Process invocation **MUST** be structured and explicit (no `sh -c` unless strictly required and justified).

---

## 8. Exception handling and resources

* Resource acquisition **MUST** use bracketed patterns (`with*`, `bracket`, `finally`) from the RIO ecosystem with correct async exception behavior.
* “Catch-all” exception handling **MUST NOT** swallow failures silently.
* Recoverable errors **SHOULD** be modeled as `Either DomainError a` at boundaries; exceptions reserved for exceptional, unrecoverable cases.

---

## 9. The AI-specific anti-loop rules for RIO

These rules are merge-blocking because RIO/Haskell AI loops are common and expensive.

### 9.1 No monad-stack reinvention

* The project **MUST NOT** introduce custom monad transformer stacks or ad-hoc effects systems without an ADR.
* Default is `RIO env`.

### 9.2 Compiler error loop breaker

If an AI attempt fails twice due to:

* missing `HasLogFunc env`,
* `MonadReader env m` / `RIO env` confusion,
* `Utf8Builder` vs `String`,
* `NoImplicitPrelude` missing exports,

then the next attempt **MUST**:

* cite the relevant authoritative RIO documentation section (or project playbook entry),
* perform an explicit assumption reset (“I was projecting base/Prelude; correct approach is RIO logging / HasLogFunc / runRIO”).

---

## 10. Project conventions (recommended defaults)

If not already decided elsewhere:

* **SHOULD** standardize on `Text` in domain types.
* **SHOULD** standardize on strict data fields (`!`) in environment records where appropriate.
* **MUST** keep imports minimal and consistent.
* **SHOULD** prefer small helpers over deeply nested `do` blocks (aligns with your “minimal indentation” preference).
