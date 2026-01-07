# Docker Security Appendix

**(Threat-Model-Driven Rules, Not Cargo Cult)**

> This appendix maps Docker rules to concrete security failure modes.
> Security here means **preventing classes of compromise**, not achieving a checklist score.

---

## Threat Classes and Controls

### 1. Supply-Chain Attacks

**Threats**

* Compromised base images
* Malicious dependency updates

**Controls**

* Pin base images (digest)
* Verify downloaded artifacts (checksums/signatures)
* Lock dependencies

---

### 2. Privilege Escalation

**Threats**

* Container breakout
* Host compromise

**Controls**

* Non-root user
* Minimal capabilities
* No `--privileged` containers

---

### 3. Secret Leakage

**Threats**

* Credentials baked into images
* Secrets exposed via layers

**Controls**

* No secrets in Dockerfile
* No secrets via build args
* Runtime injection only

---

### 4. Injection and Remote Code Execution

**Threats**

* `curl | sh`
* Executing untrusted input

**Controls**

* No remote execution without verification
* No shell-form `CMD` unless required
* No `eval` in entrypoints

---

### 5. Lateral Movement

**Threats**

* Over-exposed ports
* Flat networks

**Controls**

* Minimal port exposure
* Explicit networks
* Clear service boundaries

---

### 6. Observability Blindness

**Threats**

* Silent failure
* Hidden compromise

**Controls**

* Log to stdout/stderr
* No log suppression
* CI scanning visibility

---

## Security Merge-Blockers

A Docker change **MUST NOT** be merged if:

1. Base image is floating or undocumented
2. Container runs as root without justification
3. Secrets appear in image layers
4. Non-deterministic installs exist
5. No vulnerability scan is run

---

## Final Security Rule

If a Docker image:

* cannot be audited,
* cannot be reproduced,
* or cannot be trusted after rebuild,

then it is **not shippable**, regardless of functionality.
