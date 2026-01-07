# Engineering Standards

This directory contains the **normative engineering standards** for all projects.

## Document Precedence

In case of conflict, the hierarchy is:

1. **[Project Constitution](../CONSTITUTION.md)** (Highest authority; overrides everything below)
2. **[Universal Project Standard](STANDARD.md)**
3. **Architecture & Process** (`../architecture.md`, `../process.md`)
4. **Frontend Pack** (for UI projects)
5. **Language Addenda**
6. **Examples & Recipes** (Non-normative)

---

## 1. Universal Standard

- [STANDARD.md](STANDARD.md) — Language-agnostic project standard. All projects MUST comply.

## 2. Frontend Pack

Located in [frontend/](frontend/):

- [typed-frontend.md](frontend/typed-frontend.md) — Typed Frontend Constitution (Cross-framework invariants)
- [html.md](frontend/html.md) — HTML / Semantic Markup (The Boundary)
- [css-sass.md](frontend/css-sass.md) — CSS / Sass (Presentation Boundary)
- [examples/](frontend/examples/) — Reference examples (JSX/TSX, HTML, CSS)

## 3. Language-Specific Addenda

Located in [languages/](languages/):

- [haskell.md](languages/haskell.md) — Haskell (Functional-first, anti-OOP)
- [elm.md](languages/elm.md) — Elm / Elm Land
- [python.md](languages/python.md) — Python
- [javascript.md](languages/javascript.md) — JavaScript/Node.js
- [apl.md](languages/apl.md) — Dyalog APL Constitution

*Informative:*
- [javascript-recipes.md](languages/javascript-recipes.md) — Implementation baselines (Non-normative)

---

## Operational Documents

- [ADDENDUM_TEMPLATE.md](ADDENDUM_TEMPLATE.md) — Template and guidance for new language standards.
- [COMPLIANCE_CHECKLIST.md](COMPLIANCE_CHECKLIST.md) — Audit checklist for verifying project compliance.

## Usage

1. All team members MUST read and acknowledge the Universal Standard.
2. Apply the appropriate language addendum(s) for your project.
3. Use the compliance checklist to audit your project.
4. Document exceptions in ADRs with rationale, scope, and expiry.
5. Standards evolve via ADRs and team consensus.

---

**These standards are constitutional, not aspirational.**