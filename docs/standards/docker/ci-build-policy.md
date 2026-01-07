# CI Docker Build Policy

**(Reproducibility, Parity, Supply-Chain Control)**

> This policy defines how Docker images are built, validated, and published in CI.
> CI is the **source of truth** for Docker images.

---

## 1. Single Source of Truth

* CI **MUST** build images using the same Dockerfile as local builds.
* CI **MUST NOT** patch Dockerfile behavior dynamically.
* CI **MUST** call Docker build explicitly (no hidden wrappers).

---

## 2. Deterministic Builds (Mandatory)

CI builds **MUST** be deterministic:

* Base images pinned (tag + digest for release)
* Dependency installs pinned/locked
* No time-dependent steps

CI **MUST FAIL** if determinism cannot be guaranteed.

---

## 3. Build Arguments

* **MAY** use `ARG` for non-secret build parameters.
* **MUST NOT** pass secrets via `ARG`.
* All build args **MUST** be documented.

---

## 4. Cache Strategy (Performance Without Drift)

* CI **SHOULD** use build cache (e.g., `buildx`, registry cache).
* Cache usage **MUST NOT** change final image contents.
* Cache invalidation **MUST** be predictable.

---

## 5. Multi-Architecture Builds

If multi-arch images are required:

* **MUST** use the same Dockerfile.
* **MUST** test at least one runtime architecture.
* **SHOULD** document supported architectures explicitly.

---

## 6. Image Tagging Policy

* CI **MUST** produce:

  * immutable tags (commit SHA)
  * semantic tags (release only)
* **MUST NOT** overwrite published immutable tags.

---

## 7. Verification Gates

CI **MUST** include:

* Dockerfile linting
* Vulnerability scanning
* Policy checks (root user, secrets, size)

Failures are **merge-blocking**.

---

## Final Rule

If CI:

* builds images differently from local,
* allows non-deterministic output,
* or hides supply-chain risk,

then the pipeline **violates policy**, regardless of green builds.
