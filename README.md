# Constitutional AI-First Scaffolding

> **The Chassis for High-Integrity Software Engineering.**
> **Governed by the [Project Constitution](docs/CONSTITUTION.md).**

This is not a traditional boilerplate. It is a **governed environment** designed for a world where AI is a primary contributor. It prioritizes long-term correctness, architectural purity, and automated enforcement over short-term "copy-paste" velocity.

---

## 🏛️ The Three Pillars

### 1. Legislative: The Constitution
Everything in this repo derives authority from the **[Project Constitution](docs/CONSTITUTION.md)**.
*   **AI as Untrusted Input**: §6.1 mandates deterministic verification for all AI code.
*   **Honesty Rule**: §6.11 forbids fabrication; "I don't know" is a valid and required AI response.
*   **Language Authority**: Language-native idioms override AI "intuition."

### 2. Executive: Automated Enforcement
Rules are not suggestions; they are blocked by code.
*   **The Gatekeeper**: `make check` is the single source of truth for quality.
*   **Local Sheriff**: Strict Git Hooks (`make hooks`) enforce Conventional Commits, ban debug logs, and prevent "God Files" (>500 lines).
*   **Architectural Linter**: Physical isolation of the `Domain` layer from IO/Infrastructure.

### 3. Intelligence: Continuous Memory
AI agents are ephemeral; this repo provides them with a "brain."
*   **[AI Context Map](docs/AI_README.md)**: High-density machine instructions.
*   **[Project Active Context](docs/project_context.md)**: Living memory of current work and lessons learned.
*   **[Hallucination Log](docs/playbooks/hallucinations.md)**: Immune system record of recurring AI failures.

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
git clone <repo-url> my-project
cd my-project
make hooks          # Install the automated sheriffs
cp .env.example .env
```

### 2. Add Components
Implementation belongs in `src/`. Create subdirectories (e.g., `src/backend`) and ensure they expose the **Makefile Contract**: `fmt`, `lint`, `test`, `build`, `check`.

### 3. Develop & Verify
```bash
make fmt            # Clean up (Scripts + Components)
make check          # Pass the quality gate
```

---

## 🛠️ The AI Toolbox

| Command | Purpose |
| :--- | :--- |
| `make hooks` | Installs local enforcement (pre-commit/push). |
| `make suggest-version` | Uses AI history analysis to suggest the next SemVer. |
| `make release` | Automates the full release flow based on git log logic. |
| `./scripts/measure_loops.py` | Implements the **Assumption Reset** (§6.4) for stuck tasks. |
| `./scripts/check_architecture.py` | Audits imports to ensure the Domain remains pure. |
| `./scripts/check_complexity.py` | Blocks "God Files" and anonymous TODOs. |

---

## 📂 Project Anatomy

```text
.
├── Makefile             # Global Orchestration (The Entrypoint)
├── pyproject.toml       # Strict Python 3.14+ Governance
├── docs/                # The Legislative Branch
│   ├── CONSTITUTION.md  # Supreme Law
│   ├── AI_README.md     # AI "System Prompt"
│   └── playbooks/       # Error recovery & Hallucination logs
├── scripts/             # Internal Automation (Strictly Typed)
├── src/                 # Implementation Boundary
│   ├── backend/         # Encapsulated Haskell/FP Core
│   └── frontend/        # Encapsulated Elm/TEA UI
└── .github/             # CI & PR Templates
```

---

## ⚖️ Final Rule
If a change weakens enforcement, blurs boundaries, or relies on AI intuition over language authority, **it violates this standard**, even if it compiles.

---
*Built for the next generation of AI-assisted engineering.*