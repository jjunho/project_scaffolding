# Standards Compliance Checklist

> Use this checklist to verify a project meets the Universal Project Standard + relevant language addendum.
> Treat unmet items as blocking defects; document exceptions in an ADR.

---

## Universal Standard Compliance

### Core principles

- [ ] Code makes illegal states impossible (types, constraints, or validation)
- [ ] Effects are explicit and visible (no hidden global state, side effects)
- [ ] Code is clear, readable, and avoids unnecessary cleverness
- [ ] Correctness prioritized over optimization

### Project organization

- [ ] `README.md` at root explains purpose, build, run
- [ ] `docs/README.md` indexes all documentation
- [ ] Architecture or key decisions documented in `docs/`
- [ ] Documentation reflects current reality (not stale)

### Versioning and release

- [ ] SemVer version defined and pinned in all relevant manifests
- [ ] `CHANGELOG.md` exists in keep-a-changelog format
- [ ] Release procedure documented and followed
- [ ] Tags applied for releases

### Quality baseline

- [ ] No compiler/interpreter warnings in production builds
- [ ] No unresolved lint violations (exceptions justified)
- [ ] Code formatted consistently with project formatter
- [ ] All tests pass; no skipped tests without justification

### Testing

- [ ] New features have tests (happy path + main error cases)
- [ ] Bug fixes include regression tests
- [ ] Tests are deterministic (no flakiness)
- [ ] Unit, integration, and E2E tests organized separately

### Git hygiene

- [ ] Commits are logical, single-purpose units
- [ ] Formatting and refactors not mixed with behavior changes
- [ ] Commit messages are semantic (Conventional Commits or equivalent)
- [ ] History rewritten before merge (kept clean)
- [ ] Main branch protections enforce CI checks

### Build automation

- [ ] `fmt` target exists and works
- [ ] `lint` target exists and works
- [ ] `test` target exists and works
- [ ] `build` target exists and works
- [ ] `check` target runs all four in sequence
- [ ] `precommit` runs `check` + checks for clean working tree
- [ ] All targets are deterministic and fail-fast

### CI/CD

- [ ] CI runs fmt, lint, test, build on every PR
- [ ] CI failures block merge
- [ ] Build/dependency caching configured
- [ ] Releases only from protected branches

### Security

- [ ] No secrets in repository
- [ ] Input validated at boundaries
- [ ] Dependencies reviewed for vulnerabilities
- [ ] Sensitive data not logged

### Code review

- [ ] PRs are small and reviewable
- [ ] Reviews check for correctness, not just style
- [ ] Tests required for logic changes
- [ ] Green build required before merge

---

## Language-Specific Compliance

### Haskell (Backend)

- [ ] Code compiles with `-Wall -Werror` or equivalent
- [ ] `ormolu` formatting applied
- [ ] `hlint` violations resolved
- [ ] Haddock documentation for public APIs
- [ ] Types make illegal states impossible
- [ ] ADTs preferred over boolean flags
- [ ] Errors are values (`Either`, error types), not exceptions
- [ ] Effects explicit in types

### Elm / Elm Land

- [ ] `elm-format --validate` passes (CI)
- [ ] `elm-review` configured and passing (or N/A documented)
- [ ] `elm-test` runs and passes
- [ ] `elm-land build` succeeds
- [ ] TEA enforced (Model, Msg, update, view)
- [ ] Module boundaries enforced (Domain/, Api/, Effect/, Pages/, Components/, Shared/)
- [ ] `Domain/` does not import effects (Http, Time, ports)
- [ ] Decoders centralized in `Api/`
- [ ] Ports centralized in one module
- [ ] State modeled with ADTs (no boolean soup)
- [ ] No `Debug.*` in production code

### Python

- [ ] `black` formatting applied
- [ ] `isort` import sorting applied
- [ ] `ruff` or `flake8` linting passes
- [ ] `mypy` or `pyright` type checking passes
- [ ] Public APIs type-hinted
- [ ] `pytest` tests present and passing
- [ ] src/ layout used (no implicit working-directory imports)
- [ ] `pyproject.toml` exists with pinned dependencies
- [ ] Virtual environment documented and used
- [ ] Errors are values (Result-like, not exceptions for normal control flow)
- [ ] No wildcard imports
- [ ] No bare dictionaries as domain models

### JavaScript / Node.js

- [ ] `prettier` formatting applied
- [ ] `eslint` linting passes
- [ ] `npm audit` / security scan passes
- [ ] Tests run and pass (vitest/jest/equivalent)
- [ ] ESM used (`"type": "module"` in package.json)
- [ ] Configuration validated at startup
- [ ] `process.env` centralized in config module (not scattered)
- [ ] Async/await used consistently (no callback/promise mixing)
- [ ] Promise rejections handled (not swallowed)
- [ ] No import-time side effects (outside entrypoints)
- [ ] Domain models validated at boundaries

---

## Documentation

- [ ] All public APIs documented
- [ ] Error cases documented
- [ ] Architecture decisions recorded (ADRs)
- [ ] Deployment and operational concerns documented
- [ ] Onboarding steps documented

---

## Exceptions

For each unmet item:

- [ ] ADR or PR description documents:
  - [ ] Rationale (why exception necessary)
  - [ ] Scope (what code affected)
  - [ ] Expiry (if temporary, when resolved)

---

## Final checklist

- [ ] Project has read and acknowledged the Universal Standard
- [ ] Project has read and acknowledged relevant language addendum(ium)
- [ ] All MUST items are met or exceptions are documented
- [ ] All SHOULD items are met or exceptions are documented
- [ ] Standards are living; changes tracked in ADRs
- [ ] Team knows where to find standards (this directory)

---

**This checklist ensures consistency and enforceability across all projects.**
