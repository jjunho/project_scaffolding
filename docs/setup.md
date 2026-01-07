# Setup & Onboarding

## Universal Requirements

- **Make**: For project orchestration.
- **Git**: For version control.
- **Python 3**: For internal automation scripts.
- **Language Runtimes**: Install the specific runtimes for the components you are working on (refer to `docs/standards/languages/`).

## Trust Model

This repository optimizes for long-term correctness over short-term velocity. Expect friction at first (strict hooks, extensive checks). This is intentional to prevent technical debt accumulation.

## Environment Policy

**CI is the source of truth.** Local tooling must converge to CI behavior. If it passes locally but fails in CI, the environment is adrift.

## Local CI Verification (act)

To avoid push-fail loops on GitHub, you can run the CI pipeline locally using [act](https://github.com/nektos/act). 

1. **Install act**:
   - Manjaro/Arch: `sudo pacman -S act`
   - Other: `curl | sh` or `brew install act`
2. **Run the Quality Gate**:
   ```bash
   act -j check
   ```
This will run the GitHub Actions workflow in a local Docker container.

## Quick Start

1. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

2. **Verify Baseline**:
   Run the agnostic check to verify you have the basic tools and that the current state is valid:
   ```bash
   make status
   make check
   ```

3. **Component Initialization**:
   Each component in `src/` may have its own specialized setup. Check the `README.md` or `Makefile` within each component directory.

## IDE Recommendations

- **EditorConfig**: Install the EditorConfig plugin to honor `.editorconfig` settings automatically.
- **Git Hooks**: We recommend using the provided automation via `make check` before every commit.
- **Language Servers**: Configure the appropriate LSP for the components you are developing.

## First Run / Troubleshooting

If `make check` fails on first run:
1. **Check versions**: Ensure you are using the specific versions defined in `.tool-versions` or `package.json`.
2. **Clean artifacts**: Run `git clean -fdX` (warning: deletes all ignored files) to reset state.
3. **Inspect logs**: Failure messages usually point to specific linters or missing dependencies.

## Onboarding Checklist

- [ ] All mandatory tools installed (`make`, `git`, `python3`).
- [ ] SSH keys configured for repository access.
- [ ] `.env` file created and configured.
- [ ] `make check` passes locally.
