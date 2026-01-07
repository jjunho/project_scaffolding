# Contributing to this Scaffolding

This project is a **scaffolding template**. Contributions should focus on improving the agnostic infrastructure, standards, and automation that serve as the foundation for derived projects.

## Normative Standards

All contributions **MUST** adhere to the project standards:

- [Universal Project Standard](docs/standards/STANDARD.md)
- [Architecture & Organization](docs/architecture.md)
- [Development Process & Git Discipline](docs/process.md)

## Getting Started

1. **Environment Setup**: Follow the steps in [docs/setup.md](docs/setup.md).
2. **Understand the Architecture**: Read [docs/architecture.md](docs/architecture.md) to understand the delegation-based structure.
3. **Local Validation**: Always run `make check` before submitting a PR.

## Contribution Workflow

### 1. Propose Changes
- Open an issue for significant architectural changes.
- Smaller fixes or documentation improvements can go directly to a Pull Request.

### 2. Development
- Create a feature branch from `main`.
- Adhere to the [Build & Quality Invariant](docs/process.md#build--quality-invariant): zero warnings, zero lint errors, full formatting.
- Follow [Conventional Commits](docs/process.md#semantic-messages).

### 3. Verification
- PRs are blocked until all CI checks pass.
- Large architectural shifts require an **ADR** (Architecture Decision Record) in `docs/adrs/`.

### 4. Reviewing AI-Authored Code (The "Turing Test" for Quality)
Constitution §6 declares AI output "untrusted input". Reviewers **MUST** apply strict scrutiny:

- **Do Not Just Read**: AI code often "looks" correct but fails on edge cases. You **MUST** check out the branch and run `make check` locally.
- **Architectural Linter**: Ensure the AI has not introduced forbidden imports (e.g., Domain -> Database). Run `scripts/check_architecture.py`.
- **Assumption Check**: If the PR history shows multiple "fix" commits for the same error, verify that an **Assumption Reset** (Constitution §6.4) was performed and documented.
- **Complexity Audit**: AI tends to over-engineer. Reject "speculative generality" (interfaces with one impl, factories for simple objects).
- **Hallucination Check**: Verify that all imported libraries actually exist and are not hallucinations of similar-sounding packages.

## Quality Gate (The `make check` Contract)

Every component and the root project **MUST** implement the following targets:
- `make fmt`: Format source code.
- `make lint`: Run static analysis.
- `make test`: Execute test suites.
- `make build`: Verify buildability.
- `make check`: The canonical quality gate (runs all the above).

---
*Note: This file is part of the scaffolding. When using this template for a new project, customize this section to reflect your specific domain needs.*
