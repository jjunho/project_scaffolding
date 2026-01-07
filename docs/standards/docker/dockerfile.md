# Docker / Dockerfile Addendum

**(Reproducible Images, Explicit Boundaries, Least Privilege)**

> This document extends the Universal Project Standard for projects that use Docker.
> Dockerfiles are treated as **build boundaries** and **supply-chain artifacts**, not ad-hoc packaging scripts.
> All universal rules apply unless explicitly refined here.

---

## Scope

Applies to:

* `Dockerfile`, `Dockerfile.*` (build, runtime, CI, dev images)
* `docker/` directories (entrypoints, scripts, compose files when relevant)
* Images built locally, in CI, or published to registries

Non-goals:

* Docker is **not** a deployment strategy by itself
* Dockerfiles must not encode business logic
* Docker must not replace proper build tooling

---

## 1. Fundamental Rule (Non-Negotiable)

> A Docker image **MUST be reproducible, minimal, and explicit about trust boundaries**.

If rebuilding the same commit can produce materially different images, the Dockerfile is incorrect.

---

## 2. Base Images and Trust

### 2.1 Base image discipline

* **MUST** use explicit base images (`FROM ubuntu:24.04`, not `latest`)
* **SHOULD** pin base images by digest in production/CI images:

  ```
  FROM ubuntu:24.04@sha256:…
  ```
* **MUST** document why a base image was chosen (security, ecosystem, tooling)

### 2.2 Minimalism

* **MUST** choose the smallest viable base image
* **MUST NOT** ship build tools in runtime images
* **SHOULD** prefer distroless or slim images for runtime stages

---

## 3. Multi-Stage Builds (Mandatory)

* **MUST** use multi-stage builds for compiled or packaged artifacts
* Build dependencies **MUST NOT** leak into the final image

Pattern:

```dockerfile
FROM build-image AS build
# compile / install

FROM runtime-image
# copy artifacts only
```

Single-stage Dockerfiles are acceptable **only** for trivial tooling images.

---

## 4. Reproducible Builds

### 4.1 Determinism

* **MUST** avoid non-deterministic steps:

  * `apt upgrade`
  * floating dependency installs
  * time-dependent behavior
* **MUST** use lockfiles where applicable (npm, pip, stack, cabal, etc.)

### 4.2 Package installation discipline

* **MUST** combine package install steps to preserve cache correctness
* **MUST** clean package manager caches in the same layer

Example:

```dockerfile
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
```

---

## 5. Layering and Cache Efficiency

* **MUST** order layers from least-to-most frequently changing
* **SHOULD** copy dependency manifests before source code
* **MUST NOT** invalidate cache unnecessarily

Bad:

```dockerfile
COPY . .
RUN npm install
```

Good:

```dockerfile
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

---

## 6. Filesystem and Ownership

### 6.1 Non-root execution (Mandatory)

* **MUST** run containers as a non-root user unless technically impossible
* **MUST** document and justify any root usage

Pattern:

```dockerfile
RUN useradd -r -u 10001 appuser
USER appuser
```

### 6.2 File permissions

* **MUST** set ownership explicitly when copying files
* **MUST NOT** rely on default root ownership accidentally

---

## 7. Entrypoints and Commands

### 7.1 Explicit execution

* **MUST** use exec form for `CMD` / `ENTRYPOINT`
* **MUST NOT** rely on shell parsing unless required

Bad:

```
CMD myapp --serve
```

Good:

```
CMD ["myapp", "--serve"]
```

### 7.2 Entrypoint scripts

If entrypoint scripts exist:

* **MUST** be minimal and failure-explicit
* **MUST** use `set -euo pipefail`
* **MUST NOT** contain application logic

---

## 8. Configuration and Secrets

* **MUST NOT** bake secrets into images

* **MUST** receive configuration via:

  * environment variables
  * mounted files
  * runtime injection (CI, orchestrator)

* **MUST NOT** commit `.env` files used for secrets

* **MAY** include `.env.example` for documentation

---

## 9. Networking and Ports

* **MUST** document exposed ports
* **MUST NOT** expose ports unnecessarily
* **MUST** prefer explicit `EXPOSE` for clarity (even if optional at runtime)

---

## 10. Logging and Observability

* **MUST** log to stdout/stderr
* **MUST NOT** write logs to files inside the container
* **SHOULD** ensure logs are line-oriented and structured where possible

---

## 11. Security Baselines

* **MUST** avoid:

  * `curl | sh`
  * executing remote scripts without verification
* **MUST** verify downloaded artifacts (checksums, signatures) when feasible
* **SHOULD** scan images for vulnerabilities in CI

---

## 12. `.dockerignore` Is Mandatory

* **MUST** include `.dockerignore`
* **MUST** exclude:

  * `.git`
  * build artifacts
  * node_modules / dist / target (unless explicitly needed)
  * secrets and local config

A missing or ineffective `.dockerignore` is a merge-blocking defect.

---

## 13. CI Integration

* CI **MUST** build images using the same Dockerfile as local builds
* CI **MUST NOT** patch Dockerfile behavior dynamically
* Build args **MAY** be used but must be documented and deterministic

---

## Anti-Patterns (Merge-Blocking)

* `FROM …:latest`
* Single-stage images with build tools in runtime
* Root user without justification
* Secrets baked into images
* Non-deterministic package installs
* No `.dockerignore`
* Shell-form `CMD` without reason

---

## Reviewer Checklist (Merge-Blocking)

A Dockerfile change is approvable only if:

1. Base image is explicit and justified.
2. Multi-stage build is used when applicable.
3. Image runs as non-root.
4. Dependencies are pinned/locked.
5. Cache-friendly layer ordering is preserved.
6. No secrets are baked into the image.
7. `.dockerignore` is present and effective.

---

## Appendix — Bad vs Good vs Excellent Dockerfile

### D.1 Base image and stages

Bad:

```dockerfile
FROM ubuntu
RUN apt-get update && apt-get install -y gcc
```

Good:

```dockerfile
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends gcc
```

Excellent:

```dockerfile
FROM ubuntu:24.04 AS build
RUN apt-get update && apt-get install -y --no-install-recommends gcc

FROM ubuntu:24.04
COPY --from=build /usr/bin/myapp /usr/bin/myapp
```

---

### D.2 Root vs non-root

Bad:

```dockerfile
CMD ["myapp"]
```

Good:

```dockerfile
RUN useradd -r app
USER app
CMD ["myapp"]
```

Excellent:

```dockerfile
RUN useradd -r -u 10001 app
USER app
WORKDIR /app
CMD ["myapp"]
```

---

## Final Rule

If a Docker image:

* cannot be reproduced reliably,
* runs with unnecessary privilege,
* or hides supply-chain risk,

then it **violates this standard**, even if it “runs successfully”.
