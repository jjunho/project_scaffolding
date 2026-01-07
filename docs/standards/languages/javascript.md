# JavaScript Language Addendum

> This document extends the Universal Project Standard for JavaScript projects (Node.js and browser).
> All universal rules apply unless explicitly refined here.

## Scope

Applies to:

* Node.js services/CLIs/libraries
* Browser applications (SPA/MPA)
* Shared packages (monorepos included)

Version baseline:

* Node.js: **MUST** use an active LTS release.
* Browser: **MUST** document supported browsers and minimum versions.

If a rule is not applicable (e.g., observability for a small library), it **MUST** be marked N/A with rationale.

---

## JavaScript-specific principles

### 1. Explicit boundaries and side effects

* **MUST** isolate side effects at system boundaries (I/O, network, filesystem, DOM).
* **MUST** keep core logic pure where practical.
* **MUST** avoid import-time side effects; module top-level should not perform I/O except in entrypoints.

### 2. No "stringly-typed" domain logic

* **MUST** not model domain entities as ad-hoc objects passed around without validation.
* **MUST** validate at boundaries (HTTP, CLI args, env, storage).
* **SHOULD** centralize schemas and reuse them for runtime validation + static typing (when applicable).

### 3. Predictable async

* **MUST** use `async/await` for readability.
* **MUST** not mix callbacks/promises in the same layer.
* **MUST** not swallow promise rejections; unhandled rejections are defects.
* **SHOULD** enforce cancellation/timeouts for outbound calls.

---

## Language level and module system

* **MUST** use ESM (`"type": "module"`) unless there is a documented constraint.
* **MUST** avoid ambiguous module resolution; prefer explicit file extensions in ESM contexts where required.
* **MUST** avoid `require()`/CJS in new code unless integrating with legacy constraints.

---

## Project structure (recommended)

### Node.js service / API

```
.
├── package.json
├── README.md
├── CHANGELOG.md
├── src/
│   ├── main.js
│   ├── config/
│   ├── domain/
│   ├── adapters/
│   └── infra/
├── test/
├── docs/
├── scripts/
└── ci/
```

### Frontend app

```
.
├── package.json
├── README.md
├── CHANGELOG.md
├── src/
│   ├── app/
│   ├── features/
│   ├── components/
│   ├── routes/
│   └── styles/
├── test/
├── public/
├── docs/
└── ci/
```

Rules:

* **MUST** have a single clear entrypoint (`src/main.*`).
* **MUST** separate domain logic from adapters/IO integration.
* **MUST** avoid "misc utils" dumping grounds; utilities must have a clear owning module.

---

## Dependency and package management

* **MUST** use a lockfile and commit it (`package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock`).
* **MUST** not mix package managers in the same repo.
* **SHOULD** prefer `npm ci` / `pnpm install --frozen-lockfile` in CI.
* **MUST** justify new dependencies; remove unused dependencies routinely.

Security:

* **MUST** run dependency vulnerability checks in CI (`npm audit` or equivalent tooling).
* **MUST** review licenses for compatibility.

---

## Runtime configuration

* **MUST** validate environment configuration at startup.
* **MUST** not access `process.env.*` throughout the codebase; define a typed/config module and depend on it.
* **MUST** fail fast on missing/invalid config.

---

## Formatting, linting, and static analysis

Mandatory:

* Formatter: **Prettier**
* Linter: **ESLint**
* **SHOULD** use a modern base config and enforce consistency (no style debates in PRs).

Rules:

* **MUST** enforce formatting and linting in CI.
* **MUST** keep lint errors at zero; suppressions must be local and justified.
* **MUST** not disable rules broadly to "make CI green".

---

## Type discipline (JS without TS)

JavaScript does not have compile-time types; discipline is recovered via tooling:

* **MUST** use JSDoc for public APIs (parameters, return types, thrown errors, side effects).
* **SHOULD** enable TypeScript type-checking in "check JS" mode (`// @ts-check`) where practical.
* **MUST** validate external inputs at runtime using schemas.

If the project is large or domain-heavy, it **SHOULD** migrate to TypeScript; if not, document the rationale.

---

## Error handling

* **MUST** treat errors as part of control flow at boundaries, not sprinkled everywhere.
* **MUST** define error types (or error codes) for domain failures.
* **MUST** return actionable error messages; log context, not secrets.
* **MUST** never swallow errors in `catch` without handling or rethrowing.

Node.js specifics:

* **MUST** handle process-level failures intentionally:

  * uncaught exceptions and unhandled rejections must terminate or be escalated in a controlled way.
  * shutdown must be graceful where applicable.

---

## Async and concurrency

* **MUST** bound concurrency for batch operations (avoid unbounded `Promise.all` on large sets).
* **SHOULD** use a concurrency limiter where relevant.
* **MUST** implement request timeouts and retries with backoff where appropriate.
* **MUST** avoid "fire-and-forget" promises unless explicitly tracked.

---

## Testing

* **MUST** use a mainstream test runner (`vitest`, `jest`, or equivalent).
* **MUST** keep tests deterministic; no flaky tests tolerated.
* **MUST** separate unit tests from integration tests.
* **SHOULD** use contract tests for external integrations.
* **SHOULD** include E2E tests only for critical flows.

Frontend specifics:

* **SHOULD** prefer user-centric tests (DOM behavior) over implementation details.
* **MUST** avoid brittle snapshot tests for complex UIs; use targeted assertions.

---

## Security (JavaScript-specific)

* **MUST** avoid `eval`, `new Function`, and dynamic code execution unless strictly necessary and documented.
* **MUST** sanitize/escape untrusted input in HTML contexts to prevent XSS.
* **MUST** prevent SSRF in server-side HTTP clients via allowlists/deny lists where applicable.
* **MUST** not log secrets or PII.

---

## Observability (Node.js)

* **SHOULD** use structured logging (JSON).
* **MUST** include correlation/request IDs for request-based services.
* **SHOULD** emit metrics (latency, error rate) and tracing where relevant.

---

## Build and automation targets (JavaScript)

Projects **MUST** provide equivalents of:

* `fmt` → prettier
* `lint` → eslint
* `test` → unit/integration tests
* `build` → production build (bundler or compilation step)
* `check` → `fmt && lint && test && build`
* `precommit` → `check` + clean working tree guard

Optional but recommended:

* `typecheck` → `tsc --noEmit` (TS) or `tsc --noEmit --allowJs` (JS+JSDoc)

---

## Forbidden anti-patterns

* Import-time side effects outside entrypoints
* Unbounded concurrency (`Promise.all` on large lists) without limits
* Ad-hoc "any shape" objects as domain models without validation
* Hidden configuration (`process.env` everywhere)
* Silent `catch` blocks
* Disabling lint/format checks broadly

---

## Final JavaScript rule

If the code:

* hides side effects in modules,
* treats input as trustworthy without validation,
* relies on implicit runtime behavior,
* or allows async failures to disappear,

then it does not meet this standard, even if it runs.
