# Docker-Compose Addendum

**(Explicit Topology, Environment Isolation, Non-Production Parity)**

> This document extends the Docker / Dockerfile Addendum for projects that use `docker-compose`.
> Docker Compose is treated as a **local orchestration and integration tool**, not a deployment system.
> All universal, Dockerfile, and CI policies apply unless explicitly refined here.

---

## Scope

Applies to:

* `docker-compose.yml`, `docker-compose.*.yml`
* Local development, integration testing, ephemeral environments
* CI services spun up via Compose

Non-goals:

* Production orchestration (Kubernetes, Nomad, ECS, etc.)
* Long-lived state management
* Secrets management beyond local/dev scope

---

## 1. Fundamental Rule (Non-Negotiable)

> Docker Compose **MUST model topology and integration only**, never environment-specific logic or business rules.

If Compose is used to “decide” how the system behaves, it is misused.

---

## 2. File Strategy and Naming

* **MUST** use a base file:

  * `docker-compose.yml` → topology only
* **MAY** layer overrides:

  * `docker-compose.dev.yml`
  * `docker-compose.ci.yml`

Rules:

* Base file **MUST NOT** contain:

  * bind mounts
  * dev-only tooling
  * debug flags
* Overrides **MUST** only add/override, never contradict semantics.

Invocation pattern (documented, not enforced here):

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## 3. Services and Boundaries

* Each service **MUST** correspond to a real runtime boundary:

  * app
  * database
  * cache
  * message broker

* **MUST NOT** collapse unrelated concerns into a single service container.

* **MUST NOT** encode sequencing logic via `depends_on` as a correctness mechanism.

`depends_on` **MAY** be used for startup ordering only; readiness **MUST** be handled by the application.

---

## 4. Images vs Builds

* **MUST** prefer `image:` over `build:` in Compose.
* `build:` **MAY** be used only when:

  * image is not published yet, or
  * iteration speed requires it

If `build:` is used:

* **MUST** point to the same Dockerfile used in CI.
* **MUST NOT** embed build-only logic in Compose.

---

## 5. Volumes and Persistence

* **MUST** treat volumes as disposable unless explicitly documented.
* **MUST** document which volumes hold state and why.
* **MUST NOT** rely on implicit anonymous volumes.

Bind mounts:

* **MAY** be used for local development only.
* **MUST NOT** appear in base `docker-compose.yml`.

---

## 6. Environment Variables and Configuration

* **MUST NOT** inline secrets in Compose files.
* **MAY** use `.env` for local non-secret configuration.
* **MUST** document all required environment variables.

Rules:

* `.env` **MUST NOT** be committed if it contains secrets.
* `.env.example` **SHOULD** exist and be accurate.

---

## 7. Ports and Exposure

* **MUST** expose only required ports.
* **MUST** document port purpose.
* **MUST NOT** expose internal services unnecessarily (e.g., DB to host).

---

## 8. Networking

* **MUST** use explicit networks.
* **MUST NOT** rely on default network implicitly.
* **SHOULD** name networks semantically (`app_net`, `infra_net`).

---

## 9. Logging and Debugging

* Services **MUST** log to stdout/stderr.
* Compose **MUST NOT** redirect logs to files.
* Debug tooling **MUST** live in override files only.

---

## Anti-Patterns (Merge-Blocking)

* Using Compose as a production deployment tool
* Secrets embedded in YAML
* Base file polluted with dev-only mounts
* Business logic encoded in service definitions
* Stateful assumptions without documentation

---

## Final Rule

If `docker-compose`:

* encodes behavior instead of topology,
* leaks secrets,
* or diverges from CI/runtime assumptions,

then it **violates this standard**, even if it “works locally”.
