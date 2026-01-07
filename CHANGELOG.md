# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Initialized production-ready Haskell backend using Stack and RIO.
- Initialized standard Elm frontend.
- Implemented project-wide metadata configuration (`.project-config.yaml`) and config reader.
- Added automated Quality Gates:
  - 100% Haddock documentation coverage enforcement for Haskell.
  - "Single-Shot" optimized Haskell verification (Build + Test + Docs).
  - Clean working tree enforcement in `pre-push` hook.
  - Complexity and Hygiene gate (File size limits and strict TO-DOs).
- Implemented recursive `make clean` for deep cleanup of build artifacts (Haskell/Elm).
- Comprehensive GitHub Actions CI workflow with aggressive caching.
- Rewrote README to reflect Constitutional AI-First architecture.

### Changed
- CI workflow now builds only (quality checks enforced pre-push) and uploads backend/frontend artifacts.
