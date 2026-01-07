SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

.DEFAULT_GOAL := help

# Colors
RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
NC     := \033[0m

# --- Configuration ---
# Modules are subdirectories in src/ by default, but can be overridden
# This follows the SoC principle: core orchestration doesn't know about specific languages.
MODULES ?= $(patsubst src/%/,%,$(dir $(wildcard src/*/)))

# If src/ doesn't exist, we might have them at root (backward compatibility or small project)
ifeq ($(strip $(MODULES)),)
  # You can manually list your components here
  COMPONENTS ?= backend frontend
else
  COMPONENTS ?= $(addprefix src/,$(MODULES))
endif

# Release Info
VERSION ?= 0.0.0
TAG_PREFIX ?= v
CHANGELOG ?= CHANGELOG.md

# Scripts
SCRIPTS_DIR ?= scripts
REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
SCRIPTS_PATH := $(REPO_ROOT)/$(SCRIPTS_DIR)

# --- Guards ---
.PHONY: _guard_clean _guard_main _guard_version _guard_changelog _guard_scripts _guard_tag

_guard_scripts:
	@command -v bash >/dev/null 2>&1 || { echo "$(RED)❌ ERROR: bash required$(NC)"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)❌ ERROR: python3 required$(NC)"; exit 1; }
	@command -v git >/dev/null 2>&1 || { echo "$(RED)❌ ERROR: git required$(NC)"; exit 1; }
	@for f in \
		"$(SCRIPTS_PATH)/validate_semver.sh" \
		"$(SCRIPTS_PATH)/ensure_changelog_section.sh" \
		"$(SCRIPTS_PATH)/check_changelog.py" \
		"$(SCRIPTS_PATH)/suggest_bump.py" \
	; do \
		[[ -f "$$f" ]] || { echo "$(RED)❌ ERROR: missing script: $$f$(NC)"; exit 1; }; \
	done

_guard_python_tools:
	@if [ "$${GITHUB_ACTIONS:-}" = "true" ]; then \
		python3 -m black --version >/dev/null 2>&1 && python3 -m isort --version >/dev/null 2>&1 && python3 -m ruff --version >/dev/null 2>&1 && python3 -m mypy --version >/dev/null 2>&1 || \
			(echo "$(RED)❌ ERROR: Python modules (black, isort, ruff, mypy) missing in CI.$(NC)"; exit 1); \
	else \
		python3 -m black --version >/dev/null 2>&1 && python3 -m isort --version >/dev/null 2>&1 && python3 -m ruff --version >/dev/null 2>&1 && python3 -m mypy --version >/dev/null 2>&1 || \
			echo "$(YELLOW)⚠️  Python tools missing. Recommended: pip install black isort ruff mypy$(NC)"; \
	fi

_guard_tag:
	@tag="$(TAG_PREFIX)$(VERSION)"; \
	if git rev-parse -q --verify "refs/tags/$$tag" >/dev/null 2>&1; then \
		echo "$(RED)❌ ERROR: tag $$tag already exists$(NC)"; \
		exit 1; \
	fi

_guard_clean:
	@if [[ -n "$$(git status --porcelain)" ]]; then \
		echo "$(RED)❌ ERROR: working tree is dirty. Review changes and commit/stash first.$(NC)"; \
		exit 1; \
	fi

_guard_main:
	@branch="$$(git rev-parse --abbrev-ref HEAD)"; \
	if [[ "$$branch" != "main" && "$$branch" != "master" ]]; then \
		echo "$(RED)❌ ERROR: release must happen on main/master (current: $$branch)$(NC)"; \
		exit 1; \
	fi

_guard_version: _guard_scripts
	@if [[ "$(VERSION)" == "0.0.0" ]]; then \
		echo "$(RED)❌ ERROR: VERSION not set. Usage: make release VERSION=1.2.3$(NC)"; \
		exit 1; \
	fi
	@"$(SCRIPTS_PATH)/validate_semver.sh" "$(VERSION)" >/dev/null 2>&1 || { \
		echo "$(RED)❌ ERROR: invalid VERSION. Use SemVer x.y.z$(NC)"; \
		exit 1; \
	}

_guard_changelog: _guard_scripts
	@"$(SCRIPTS_PATH)/ensure_changelog_section.sh" "$(CHANGELOG)" "$(VERSION)" >/dev/null 2>&1 || { \
		echo "$(RED)❌ ERROR: $(CHANGELOG) is missing section '## [$(VERSION)]'.$(NC)"; \
		exit 1; \
	}

# --- Core Tasks (Delegation) ---
# Each target propagates to components. If a component has a Makefile, it is invoked.
.PHONY: fmt lint test build check precommit status

status:
	@git status --short
	@echo -e "\n$(YELLOW)Components searched in: $(COMPONENTS)$(NC)"

define delegate
	@for comp in $(COMPONENTS); do \
		if [[ -f "$$comp/Makefile" ]]; then \
			echo -e "\n$(BLUE)▶ Executing $(1) in $$comp...$(NC)"; \
			$(MAKE) -C $$comp $(1) VERSION=$(VERSION); \
		elif [[ -d "$$comp" ]]; then \
			echo "$(YELLOW)⚠️  Skipping $(1) in $$comp: no Makefile$(NC)"; \
		fi; \
	done
endef

fmt: _guard_python_tools
	@if command -v black >/dev/null 2>&1; then \
		echo -e "$(BLUE)▶ Formatting scripts/ (black + isort)...$(NC)"; \
		python3 -m black scripts; python3 -m isort scripts; \
	fi
	$(call delegate,fmt)

lint: _guard_python_tools
	@echo -e "$(BLUE)▶ Architectural Check...$(NC)"
	@python3 scripts/check_architecture.py
	@if command -v ruff >/dev/null 2>&1; then \
		echo -e "$(BLUE)▶ Linting scripts/ (ruff + mypy)...$(NC)"; \
		python3 -m ruff check scripts; python3 -m mypy scripts; \
	fi
	$(call delegate,lint)

test:
	$(call delegate,test)

build:
	$(call delegate,build)

clean:
	@echo -e "$(BLUE)▶ Cleaning root artifacts...$(NC)"
	@rm -rf .mypy_cache .ruff_cache
	@find . -name "__pycache__" -type d -exec rm -rf {} +
	$(call delegate,clean)

check: _guard_python_tools
	@if command -v black >/dev/null 2>&1; then \
		echo -e "$(BLUE)▶ Formatting scripts/ (black + isort)...$(NC)"; \
		black scripts; isort scripts; \
	fi
	@echo -e "$(BLUE)▶ Architectural Check...$(NC)"
	@python3 scripts/check_architecture.py
	@if command -v ruff >/dev/null 2>&1; then \
		echo -e "$(BLUE)▶ Linting scripts/ (ruff + mypy)...$(NC)"; \
		ruff check scripts; mypy scripts; \
	fi
	$(call delegate,check)
	@echo -e "\n$(GREEN)✅ OK: All checks passed.$(NC)"

precommit: _guard_clean check
	@echo -e "\n$(GREEN)✅ OK: Ready to commit.$(NC)"

hooks:
	@git config core.hooksPath scripts/git-hooks
	@echo -e "$(GREEN)✅ Git hooks installed (core.hooksPath = scripts/git-hooks)$(NC)"

# --- Release Workflow ---
.PHONY: release changelog-check changelog-lint bump-version suggest-version

suggest-version: _guard_scripts
	@python3 "$(SCRIPTS_PATH)/suggest_bump.py"

changelog-lint: _guard_scripts
	@python3 "$(SCRIPTS_PATH)/check_changelog.py" "$(CHANGELOG)" --require-unreleased --require-dates
	@echo "$(GREEN)✅ CHANGELOG lint passed.$(NC)"

changelog-check: _guard_version _guard_changelog changelog-lint
	@echo "$(GREEN)✅ CHANGELOG is ready for $(VERSION).$(NC)"

bump-version:
	@if [[ "$(VERSION)" == "0.0.0" ]]; then \
		V=$$(python3 "$(SCRIPTS_PATH)/suggest_bump.py" | grep "Next Version:" | awk '{print $$NF}' | sed 's/v//'); \
		$(MAKE) bump-version VERSION=$$V; \
	else \
		$(call delegate,bump-version); \
	fi

release: _guard_clean _guard_main
	@if [[ "$(VERSION)" == "0.0.0" ]]; then \
		V=$$(python3 "$(SCRIPTS_PATH)/suggest_bump.py" | grep "Next Version:" | awk '{print $$NF}' | sed 's/v//'); \
		echo -e "$(BLUE)🚀 No VERSION specified. Suggested: $$V$(NC)"; \
		read -p "Use $$V? [y/N] " confirm; \
		if [[ $$confirm == [yY] ]]; then \
			$(MAKE) release VERSION=$$V; \
		else \
			echo "Release aborted."; exit 1; \
		fi \
	else \
		$(MAKE) _guard_version _guard_tag changelog-check bump-version check; \
		git add -A; \
		git commit -m "chore(release): $(VERSION)"; \
		git tag "$(TAG_PREFIX)$(VERSION)"; \
		echo -e "\n$(GREEN)✅ Release $(VERSION) tagged successfully.$(NC)"; \
		echo "$(YELLOW)Next: git push && git push --tags$(NC)"; \
	fi

# --- Help ---
.PHONY: help
help:
	@echo -e "$(GREEN)Language-Agnostic High-Quality Scaffolding$(NC)"
	@echo "Rules: clean repo, specific commits, automated gates."
	@echo ""
	@echo "Commands:"
	@echo "  make fmt         Format all components"
	@echo "  make lint        Lint all components"
	@echo "  make test        Test all components"
	@echo "  make build       Build all components"
	@echo "  make check       Gate: fmt + lint + test + build"
	@echo "  make clean       Remove build artifacts"
	@echo "  make status      Git status + detected components"
	@echo "  make precommit   Require clean tree + make check"
	@echo "  make hooks       Install git hooks (local enforcement)"
	@echo "  make suggest-version  Suggest next SemVer based on git log"
	@echo "  make release     Full release flow (auto-calculates version if missing)"
