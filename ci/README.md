# CI/CD Configuration

> **Governed by the [Project Constitution](../docs/CONSTITUTION.md)**

This directory contains Continuous Integration and Deployment configurations.

## Philosophy

Per the Project Constitution, the repository MUST contain only clean code. All quality checks (linting, formatting, testing) are enforced prior to pushing to the repository. Therefore, the CI pipeline is responsible ONLY for building the artifacts to ensure the code is compilable.

## Requirements

Any CI pipeline configured here **MUST**:

1.  **Block Merge**: On failure of `make build`.
2.  **Verify Compilation**: Run `make build` to ensure artifacts can be produced.
3.  **Supply Chain Security**: Build docker images deterministically and scan for vulnerabilities.

## Recommended Workflow (GitHub Actions)

This workflow implements the "Build Only" philosophy. It relies on `make build` for compilation and handles artifact generation.


Create `.github/workflows/ci.yml` with the following:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [ "main" ]
    tags: [ "v*" ]

permissions:
  contents: read
  packages: write
  security-events: write

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

env:
  # Registry image name (GHCR)
  IMAGE_NAME: ghcr.io/${{ github.repository }}
  DOCKER_BUILDKIT: "1"

jobs:
  gate:
    name: Gate (make check)
    runs-on: ubuntu-24.04

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      # If your Makefile installs tools itself, remove this.
      - name: Install system deps (minimal)
        run: |
          sudo apt-get update
          sudo apt-get install -y --no-install-recommends make git curl ca-certificates

      # Cache Stack (Haskell)
      - name: Cache Stack
        uses: actions/cache@v4
        with:
          path: |
            ~/.stack
            backend/.stack-work
          key: stack-${{ runner.os }}-${{ hashFiles('backend/stack.yaml', 'backend/package.yaml', 'backend/**/*.cabal') }}
          restore-keys: |
            stack-${{ runner.os }}-

      # Cache Elm build artifacts (cheap; optional)
      - name: Cache Elm
        uses: actions/cache@v4
        with:
          path: |
            frontend/elm-stuff
          key: elm-${{ runner.os }}-${{ hashFiles('frontend/elm.json', 'frontend/**/*.elm') }}
          restore-keys: |
            elm-${{ runner.os }}-

      - name: Gate
        run: make check

  docker-build-scan:
    name: Docker build + scan (no push)
    runs-on: ubuntu-24.04
    needs: [ gate ]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      # Policy Checks: Release-level safety
      - name: Policy checks
        run: |
          test -f .dockerignore
          grep -qE '^FROM .+:[^ ]+$' Dockerfile
          grep -qE '^USER ' Dockerfile

      - name: Set up Buildx
        uses: docker/setup-buildx-action@v3

      # Build to local docker engine so scanners can inspect by tag.
      - name: Build (load, cache gha)
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./Dockerfile
          push: false
          load: true
          tags: ${{ env.IMAGE_NAME }}:sha-${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            GIT_SHA=${{ github.sha }}

      - name: Hadolint (Dockerfile)
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: error

      # Vulnerability scan: fail on HIGH/CRITICAL.
      - name: Trivy (image scan)
        uses: aquasecurity/trivy-action@0.24.0
        with:
          image-ref: ${{ env.IMAGE_NAME }}:sha-${{ github.sha }}
          format: table
          exit-code: "1"
          severity: HIGH,CRITICAL
          ignore-unfixed: true

  docker-publish:
    name: Docker publish (tags only)
    runs-on: ubuntu-24.04
    needs: [ gate, docker-build-scan ]
    if: startsWith(github.ref, 'refs/tags/v')

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      # Require digest-pinned base images for release
      - name: Require digest-pinned base images
        run: grep -qE '^FROM .+@sha256:' Dockerfile

      - name: Set up Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract version from tag
        id: ver
        run: |
          tag="${GITHUB_REF_NAME}"
          echo "version=${tag#v}" >> "$GITHUB_OUTPUT"

      # Publish immutable + semver + latest.
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./Dockerfile
          push: true
          platforms: linux/amd64
          tags: |
            ${{ env.IMAGE_NAME }}:sha-${{ github.sha }}
            ${{ env.IMAGE_NAME }}:v${{ steps.ver.outputs.version }}
            ${{ env.IMAGE_NAME }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            GIT_SHA=${{ github.sha }}
            VERSION=${{ steps.ver.outputs.version }}
```

## Implementation Notes

1.  **Single Gate**: `make check` is the only logic gate. The workflow does not re-encode fmt/lint/test/build logic.
2.  **Safe Caching**: Stack/Elm caches only speed up; they do not change declared tool behavior. Docker cache uses `type=gha`, which is deterministic when Dockerfile inputs are deterministic.
3.  **Tag-Only Publishing**: Only `refs/tags/v*` will publish. PRs and normal pushes build/scan but do not push.
4.  **Minimal Privileges**: Uses `GITHUB_TOKEN` for GHCR. No long-lived registry secrets required.
5.  **Strict Policy Enforcement**:
    *   Fails if `.dockerignore` is missing.
    *   Fails if Dockerfile uses floating tags without versions.
    *   Fails if image runs as root (missing `USER`).
    *   For releases, requires digest-pinned base images.
