# Bash Language Addendum

**(Shell-Strict, Failure-Explicit, Boundary-First)**

> This document extends the Universal Project Standard for Bash/shell scripting.
> It exists to prevent “works on my machine” scripts, silent failures, and environment-coupled behavior.
> Bash is treated as **boundary glue**: orchestration, automation, and integration—not domain logic.

---

## Scope

Applies to:

* Bash scripts (`#!/usr/bin/env bash`) committed to the repository (`scripts/`, CI helpers, release tooling, dev tooling).
* Shell code embedded in CI YAML.
* Any script that runs in developer machines, CI, or production-like automation environments.

Out of scope (must not be implemented in Bash):

* Core domain logic
* Non-trivial data transformations
* Stateful services

If the script is larger than “thin orchestration”, use a real language (Python, Haskell, etc.).

---

## 1. Fundamental Rule (Non-Negotiable)

> Bash scripts **MUST** be deterministic, failure-explicit, and environment-minimizing.

A Bash script is acceptable only when:

* it orchestrates commands,
* it validates inputs and environment,
* it is safe by default.

If it needs complex parsing, rich error types, or non-trivial state, it is the wrong tool.

---

## 2. Script Safety Baseline (Merge-Blocking)

Every Bash script **MUST** start with:

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

Rules:

* **MUST** use `bash`, not `sh`.
* **MUST** enable strict mode: `set -euo pipefail`.
* **MUST** set a safe `IFS` as shown.
* **MUST** avoid relying on undefined variables (`set -u` enforces this).
* **MUST NOT** suppress errors (`|| true`) except with explicit justification and localized scope.

---

## 3. Inputs are Untrusted (Boundary Discipline)

### 3.1 Argument and environment validation is mandatory

* **MUST** validate required arguments.
* **MUST** validate environment variables used by the script.
* **MUST** produce a clear usage/help message on failure.

Minimum pattern:

```bash
usage() {
  cat <<'EOF'
usage: script-name [options] <arg>
EOF
}

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

[[ $# -ge 1 ]] || { usage >&2; die "missing required arg"; }
```

### 3.2 Paths and working directory are explicit

* **MUST** not assume a current working directory.

* **MUST** either:

  * compute repo root deterministically, or
  * require explicit paths from caller.

* **MUST** quote all paths.

---

## 4. Output is a Contract

* **MUST** write human-facing logs to stderr on failure.
* **MUST** keep stdout clean when stdout is intended for piping.
* **SHOULD** provide `--json` or machine-readable mode if scripts are used by other automation.

Rules:

* **MUST** not mix progress chatter with machine output.
* **MUST** use consistent log formatting for CI readability.

Recommended helpers:

```bash
log()  { printf '%s\n' "$*" >&2; }
warn() { printf 'warning: %s\n' "$*" >&2; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }
```

---

## 5. Quoting and Word Splitting (Hard Rules)

* **MUST** quote variable expansions unless you intentionally want splitting/globbing.
* **MUST** use arrays for lists of paths/args.
* **MUST NOT** use `for x in $(...)` (word-splitting bug).

Bad:

```bash
for f in $(ls *.hs); do
  echo $f
endone
```

Good:

```bash
shopt -s nullglob
files=( *.hs )
for f in "${files[@]}"; do
  printf '%s\n' "$f"
done
```

---

## 6. Pipelines and Error Propagation

* **MUST** rely on `pipefail` so pipeline failures are not masked.
* **MUST** not ignore exit codes of critical commands.

If a command can fail and that failure is acceptable, it **MUST** be handled explicitly:

```bash
if ! cmd; then
  warn "cmd failed; continuing because …"
fi
```

---

## 7. Temporary Files and Cleanup

* **MUST** use `mktemp` for temp files/dirs.
* **MUST** install a cleanup trap for temp resources.

Pattern:

```bash
tmp_dir="$(mktemp -d)"
cleanup() { rm -rf "$tmp_dir"; }
trap cleanup EXIT
```

* **MUST** avoid writing to predictable temp paths (`/tmp/foo`) without unique suffixes.

---

## 8. Security Baselines

* **MUST** not `curl | bash`.
* **MUST** not execute untrusted input.
* **MUST** not interpolate untrusted strings into `eval`.
* **MUST** treat shell injection as a primary risk.

Forbidden:

```bash
eval "$USER_INPUT"
```

If you think you need `eval`, you almost certainly need a different language.

---

## 9. Portability and Tooling Assumptions

### 9.1 Explicit dependencies

* **MUST** document required external tools (e.g., `git`, `jq`, `curl`) at top of script or in usage.
* **MUST** fail fast with a clear message if a required tool is missing.

Pattern:

```bash
need_cmd() { command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"; }
need_cmd git
need_cmd jq
```

### 9.2 OS-specific behavior

* **MUST** not rely on GNU vs BSD differences without detection.
* **MAY** branch by platform, but such branches **MUST** be explicit and tested in CI if relevant.

---

## 10. Style and Maintainability

### 10.1 Functions and structure

* **MUST** organize scripts as:

  * constants + helpers
  * argument parsing
  * main logic in a `main` function

Recommended shape:

```bash
main() {
  parse_args "$@"
  run
}
main "$@"
```

### 10.2 No deep indentation

* **SHOULD** avoid nesting by using:

  * early returns
  * guard clauses
  * helper functions

### 10.3 Prefer `printf` over `echo`

* **MUST** prefer `printf` (portable and predictable).

---

## 11. Linting and Formatting

* **MUST** pass `shellcheck` with no warnings in CI.
* **SHOULD** use `shfmt` for formatting.
* **MUST** treat shellcheck failures as merge-blocking.

---

## 12. Anti-Patterns (Merge-Blocking)

* `#!/bin/sh` for non-trivial scripts
* Missing `set -euo pipefail`
* Unquoted expansions (`$var`) in paths/args
* `for x in $(...)`
* `eval`, `source` of untrusted content
* silent error swallowing (`|| true`) without justification
* writing secrets to logs
* scripts that implement business logic

---

## Reviewer Checklist (Merge-Blocking)

A script is approvable only if:

1. Uses `#!/usr/bin/env bash` and strict mode.
2. Validates args/env and provides usage.
3. Quotes expansions; uses arrays for lists.
4. Handles errors intentionally; no masked failures.
5. Uses mktemp + trap for temp resources.
6. Lists required tools and fails fast if missing.
7. Passes `shellcheck` (and `shfmt` if used).

---

## Final Rule

If the script:

* can silently succeed while failing internally,
* depends on implicit environment state,
* or could inject/execute untrusted content,

then it **violates this standard**, even if it “works locally”.

---

## Appendix — Bad vs Good vs Excellent Bash

This appendix is designed to be reviewer-grade: each pattern corresponds to a merge-blocking failure mode or a strongly recommended discipline in the Bash addendum.

---

### A.1 Script header and strict mode

Bad (silent failures, undefined vars, pipeline masking)

```bash
#!/bin/bash
echo "Starting..."
cmd_a | cmd_b
rm $TMPDIR/file
```

Good (strict mode, safe IFS, predictable failures)

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

echo "Starting..." >&2
cmd_a | cmd_b
rm -f "${TMPDIR}/file"
```

Excellent (structured entrypoint + helpers)

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

log() { printf '%s\n' "$*" >&2; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

main() {
  log "Starting..."
  cmd_a | cmd_b
}

main "$@"
```

---

### A.2 Usage, argument validation, and guard clauses

Bad (mysterious failure later)

```bash
target="$1"
cp file "$target"
```

Good (usage + explicit validation)

```bash
usage() {
  cat <<'EOF'
usage: deploy.sh <target-dir>
EOF
}

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

[[ $# -eq 1 ]] || { usage >&2; die "expected 1 argument"; }
target="$1"

cp file "$target"
```

Excellent (validate semantics, not only presence)

```bash
[[ -d "$target" ]] || die "target must be an existing directory: $target"
[[ -w "$target" ]] || die "target is not writable: $target"
```

---

### A.3 Quoting and word splitting (paths with spaces)

Bad (breaks on spaces; glob expansion risk)

```bash
rm -rf $dir/*
cp $src $dst
```

Good

```bash
rm -rf "${dir:?}"/*
cp -- "$src" "$dst"
```

Excellent (defensive: reject empty dir, explicit error)

```bash
[[ -n "${dir:-}" ]] || die "dir not set"
[[ -d "$dir" ]] || die "dir not a directory: $dir"
rm -rf -- "${dir:?}"/*
```

---

### A.4 “for x in $(…)” (classic bug)

Bad (splits on whitespace; breaks on newlines)

```bash
for f in $(git ls-files); do
  echo "$f"
done
```

Good (read line-by-line)

```bash
git ls-files | while IFS= read -r f; do
  printf '%s\n' "$f"
done
```

Excellent (NUL-safe for arbitrary filenames)

```bash
git ls-files -z | while IFS= read -r -d '' f; do
  printf '%s\n' "$f"
done
```

Reviewer note: NUL-safe is preferred when filenames can be arbitrary.

---

### A.5 Arrays for argument lists

Bad (loses structure; splits unexpectedly)

```bash
args="--foo $value --bar $other"
mycmd $args
```

Good

```bash
args=( --foo "$value" --bar "$other" )
mycmd "${args[@]}"
```

Excellent (conditionally add flags without branching mess)

```bash
args=( --foo "$value" )
[[ -n "${other:-}" ]] && args+=( --bar "$other" )
mycmd "${args[@]}"
```

---

### A.6 Pipelines and failure propagation

Bad (failure in cmd_a ignored if cmd_b succeeds)

```bash
cmd_a | cmd_b
echo "done"
```

Good (pipefail already set; failure propagates)

```bash
cmd_a | cmd_b
printf '%s\n' "done" >&2
```

Excellent (explicit handling when failure is acceptable)

```bash
if ! cmd_a | cmd_b; then
  warn "cmd pipeline failed; continuing because <reason>"
fi
```

---

### A.7 Temporary files and cleanup traps

Bad (predictable temp path; no cleanup)

```bash
tmp="/tmp/output.txt"
do_work > "$tmp"
```

Good (mktemp + cleanup)

```bash
tmp="$(mktemp)"
cleanup() { rm -f "$tmp"; }
trap cleanup EXIT

do_work > "$tmp"
```

Excellent (temp dir + robust cleanup)

```bash
tmp_dir="$(mktemp -d)"
cleanup() { rm -rf "$tmp_dir"; }
trap cleanup EXIT

out="$tmp_dir/output.txt"
do_work > "$out"
```

---

### A.8 Detect required tools (fail fast)

Bad (fails later with confusing error)

```bash
jq '.x' file.json
```

Good

```bash
need_cmd() { command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"; }
need_cmd jq

jq '.x' file.json
```

Excellent (version constraints when relevant)

```bash
need_version() {
  local cmd="$1" want="$2"
  local got
  got="$("$cmd" --version 2>/dev/null | head -n1 || true)"
  [[ "$got" == *"$want"* ]] || die "require $cmd version containing '$want' (got: $got)"
}
```

---

### A.9 Safe deletion (avoid catastrophic rm)

Bad (rm -rf on possibly empty var)

```bash
rm -rf "$TARGET_DIR"
```

Good (require non-empty, use :? guard)

```bash
rm -rf -- "${TARGET_DIR:?}"
```

Excellent (extra sanity checks)

```bash
[[ "$TARGET_DIR" != "/" ]] || die "refusing to delete /"
[[ -d "$TARGET_DIR" ]] || die "not a directory: $TARGET_DIR"
rm -rf -- "${TARGET_DIR:?}"
```

---

### A.10 Subshell and `cd` safety

Bad (cd failure ignored; relative path surprises)

```bash
cd "$dir"
make build
```

Good

```bash
cd "$dir"
make build
```

Excellent (subshell confines directory change)

```bash
(
  cd "$dir"
  make build
)
```

Reviewer note: subshell is preferred to avoid leaking working directory changes.

---

### A.11 Reading files safely

Bad (breaks on whitespace/backslashes)

```bash
while read line; do
  echo "$line"
done < file.txt
```

Good

```bash
while IFS= read -r line; do
  printf '%s\n' "$line"
done < file.txt
```

Excellent (explicit encoding/format expectations)

```bash
[[ -f file.txt ]] || die "missing file: file.txt"
while IFS= read -r line; do
  printf '%s\n' "$line"
done < file.txt
```

---

### A.12 `echo` vs `printf`

Bad (echo varies across shells; escapes differ)

```bash
echo "\tHello"
```

Good

```bash
printf '\t%s\n' "Hello"
```

Excellent (stderr vs stdout discipline)

```bash
printf '%s\n' "progress: Hello" >&2
printf '%s\n' "machine-output"  # stdout
```

---

### A.13 “Ignore failures” (`|| true`) done correctly

Bad (masks real failures)

```bash
rm -rf build || true
```

Good (justify and scope)

```bash
rm -rf build 2>/dev/null || true  # acceptable: missing dir is fine
```

Excellent (prefer explicit intent over blanket ignore)

```bash
if [[ -d build ]]; then
  rm -rf -- build
fi
```

---

### A.14 Avoid `eval` (injection hazard)

Bad (command injection)

```bash
eval "$USER_INPUT"
```

Good (case dispatch)

```bash
case "${ACTION:-}" in
  build) make build ;; 
  test)  make test ;; 
  *) die "unknown action: ${ACTION:-<unset>}" ;; 
esac
```

Excellent (explicit allowed set + clear usage)

```bash
usage() { printf '%s\n' "usage: script.sh --action {build|test}" >&2; }
```

---

### A.15 Minimal argument parsing (without getting fancy)

Bad (positional ambiguity)

```bash
mode="$1"
shift
```

Good (simple flags)

```bash
MODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="${2:-"")"; shift 2 ;; 
    -h|--help) usage; exit 0 ;; 
    *) die "unknown arg: $1" ;; 
  esac
done

[[ -n "$MODE" ]] || die "--mode is required"
```

Excellent (allow defaults but keep explicit)

```bash
MODE="${MODE:-check}"  # env default allowed if documented
```

---

## Appendix — Reviewer merge-blockers (Bash)

A Bash PR fails review if any of the following are true:

1. Missing `#!/usr/bin/env bash`, `set -euo pipefail`, or safe `IFS`.
2. Unquoted expansions used in paths/args.
3. Uses `for x in $(...)` (must be read loop or arrays; prefer NUL-safe where needed).
4. Uses `eval`, or executes untrusted input.
5. Deletes/mutates paths without `:?` guards or sanity checks.
6. Temporary files created without `mktemp` + `trap` cleanup.
7. No usage/help and no validation for required args/env.
8. Does not pass `shellcheck` in CI.
