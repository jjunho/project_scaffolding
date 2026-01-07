# Elm / Elm Land Language Addendum

> **This document extends the Universal Project Standard for Elm projects, with specific conventions for Elm Land.**
> All universal rules apply unless explicitly refined here.

---

## Scope

Applies to:

* Elm single-page applications (SPAs), multi-page apps (MPAs), and embedded Elm modules
* Elm Land projects (recommended when applicable)

Baseline:

* Elm compiler version **MUST** be pinned in `elm.json`.
* Node.js version **SHOULD** be pinned (via `.nvmrc`, `.tool-versions`, or CI image pin) to prevent JS toolchain drift.
* elm-land version **MUST** be pinned in `package.json` and lockfile; CI **MUST** use lockfile (`npm ci` or `pnpm i --frozen-lockfile`).
* Build-time scripts and codegen tools **MUST** have pinned versions and be run as part of `build` and `check` targets.
* Tooling versions **SHOULD** be pinned (via lockfile if managed by npm/pnpm) to avoid drift.

Rationale: Unpinned Node or elm-land versions cause "works on my machine" failures and platform-specific build outputs.

If a rule is N/A (e.g., observability for a purely static frontend), it **MUST** be documented as such, with rationale.

---

## 1. Core principles (Elm-specific)

### 1.1 Make illegal states unrepresentable (mandatory)

* **MUST** model domain state using custom types and records that make invalid states impossible.
* **MUST** prefer `Maybe`/`Result` over sentinel values and "empty string means missing" conventions.
* **MUST** validate at boundaries (ports, HTTP, flags) and represent validated state explicitly.

### 1.2 Effects are explicit (mandatory)

* **MUST** keep all side effects inside `Cmd`/`Sub` and Elm Land's boundary mechanisms (routes, effects, ports).
* **MUST NOT** hide effects in helper functions via implicit global assumptions.
* **MUST** isolate ports: a dedicated module (`Ports.elm` or `Effect/Ports.elm`) is the only place where port messages are encoded/decoded.

### 1.3 Clarity over cleverness (mandatory)

* **MUST** keep update logic readable and linear.
* **SHOULD** avoid deep nesting; refactor into helpers.
* **MUST** avoid "mega modules"; split by feature/boundary.

---

## 1.4 Boundary taxonomy (fundamental concept)

**Boundary**: Any module/function that translates between untrusted external inputs and trusted internal domain values.

External inputs include: HTTP responses, port messages, URL params, flags, localStorage, JS events.

**Merge-blocking rules:**

* **MUST**: Untrusted inputs are decoded/parsed and then **validated** before they enter Domain state.
* **MUST NOT**: Domain values contain `Json.Decode.Value`, `Json.Encode.Value`, `Url`, `Navigation.Key`, raw flags, or port payloads.
* **MUST NOT**: Domain types model routing, navigation, layout, or view-only concerns (e.g., `Tab`, `ModalState`, `ExpandedSections`, `PageNumber`). Domain represents business concepts and invariants; UI state belongs in `Pages/Layouts/Components`.
* **MUST**: All boundary translation happens in `Api/`, `Effect/`, or `Pages/` — never in `Domain/`.

Rationale: This prevents "proto-domain" values and UI concerns from leaking into internal logic, keeping domain invariants testable without I/O and business logic pure.

---

## 2. Project structure (Elm Land)

Elm Land already provides a strong convention. The project **MUST** keep Elm code under `src/` and treat generated artifacts as build outputs.

Recommended structure:

```
.
├── README.md
├── CHANGELOG.md
├── Makefile
├── elm.json
├── package.json
├── src/
│   ├── Pages/                (Elm Land routes; SHOULD NOT exceed ~300-500 LOC or >20 Msg constructors)
│   ├── Layouts/              (Elm Land layouts, if used)
│   ├── Components/           (shared UI components; SHOULD NOT exceed ~300-500 LOC)
│   ├── Domain/               (domain types + pure logic; SHOULD NOT exceed ~300-500 LOC per module)
│   ├── Api/                  (HTTP boundary, decoders/encoders)
│   ├── Effect/               (commands, ports boundary wrappers)
│   └── Shared/               (shared helpers, Remote, Error, time, config)
├── tests/
│   └── ...                   (elm-test)
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── setup.md
│   └── adrs/
└── ci/
```

**Module size heuristic:** If a module exceeds ~300–500 LOC or >20 Msg constructors, it **SHOULD** be split by subdomain. If not splitting, the PR **MUST** justify why cohesion remains high. (This is guidance, not a hard rule; use judgment.)

Rules:

* **MUST** keep domain logic (`Domain/`) pure (no HTTP, no ports, no time).
* **MUST** keep decoders/encoders close to boundaries (`Api/`, `Effect/`, ports).
* **MUST** avoid "Utils.elm" dumping grounds; helpers must live near the feature/boundary they serve.

---

### 2.1 Feature slicing (recommended for larger apps)

When the app exceeds a few pages, organize by feature while preserving boundary rules:

```
src/
Features/
  User/
    Domain.elm
    Api.elm
    Update.elm
    View.elm
  Billing/
    Domain.elm
    Api.elm
    ...
Pages/              (routes, delegating to Feature modules)
```

Rules:

* Feature `Domain/` modules follow strict domain rules (pure, no boundaries).
* `Pages/` route handlers orchestrate features; features do **not** import `Pages/`.
* Each feature's `Api/`, `Update/`, `View/` are isolated to that feature.

This pattern prevents "god Pages" as the app grows.

---

## 3. Tooling and Dependencies

### 3.1 Dependency Management (Critical)

* **MUST** use standard CLI tools (`elm`, `elm-land`) to manage dependencies.
* **MUST NOT** edit `elm.json` manually.

**Why?** Manual edits frequently break the dependency solver, resulting in this error:

> It looks like the dependencies elm.json in were edited by hand (or by a 3rd
> party tool) leaving them in an invalid state.
>
> Try to change them back to what they were before! It is much more reliable to
> add dependencies with elm install or the dependency management tool in
> elm reactor.

**Correct Usage:**

* `elm install <package>`
* `elm-land add page ...`

### 3.2 Formatter

* **MUST** run `elm-format` across all Elm sources.
* **MUST** treat formatting drift as merge-blocking.
* CI: **MUST** use `elm-format --validate` (never auto-write on CI).

### 3.2 Lint / review

* **SHOULD** use `elm-review` with a committed `review/` configuration.
* **MUST** keep review clean; rule suppressions must be local and justified.
* Recommended review rules (policy-level intent):

  * No unused dependencies/modules
  * No debug leftovers in production
  * Enforce module boundaries (e.g., ports isolated)

### 3.3 Compilation

* **MUST** compile with zero compiler errors. Elm has no conventional warnings; any compiler error is merge-blocking.

---

## 4. Testing

* **MUST** use `elm-test` for pure logic, decoders, and update invariants.
* **SHOULD** test JSON decoders with both happy path and failure cases.
* **MUST** keep tests deterministic.
* **SHOULD** prefer property-based testing where it increases confidence (e.g., invariants on domain transformations).

---

## 5. HTTP, JSON, and boundaries

* **MUST** treat JSON decoding as a security/correctness boundary:

  * Decode strictly
  * Fail explicitly
  * Surface actionable error states in the model
* **MUST** not "partially decode" and then assume fields exist later.
* **SHOULD** centralize API endpoints and request/response types in `Api/`.

---

## 6. Boundary policy (non-negotiable)

Elm's strongest advantage is explicit boundaries. The project **MUST** preserve that by forbidding boundary leakage.

### 6.1 Allowed dependency directions (layering)

Define layers:

* `Domain/` = domain types + pure transformations
* `Api/` = HTTP boundary (endpoints, requests, decoders/encoders)
* `Effect/` = commands/ports/time/random wrappers (boundary adapters)
* `Pages/`, `Layouts/` = TEA orchestration + routing integration
* `Components/` = view-only or view + local state (no app-wide effects)
* `Shared/` = small cross-cutting pure helpers

Rules:

* **MUST**: `Domain/` imports only:

  * Elm core packages (`Basics`, `List`, `Dict`, `Set`, `Maybe`, `Result`, etc.)
  * other `Domain/*`
  * *optionally* a *strictly* pure helper subset of `Shared/*`
* **MUST NOT**: `Domain/` import any of:

  * `Http`, `Json.Decode`, `Json.Encode`, `Time`, ports, `Browser`, Elm Land routing modules, or `Effect/*`
* **MUST**: `Api/` may import `Domain/`, `Json.Decode`, `Json.Encode`, `Http`
* **MUST**: `Effect/` may import `Api/`, `Domain/`, boundary modules (`Time`, `Random`, ports)
* **MUST**: `Pages/` and `Layouts/` **MUST NOT** import `Http`, `Json.Decode`, `Json.Encode`, or `Ports` directly.
  * All effects **MUST** be obtained via `Effect/*` wrappers and `Api/*` functions.
  * This enforces thin Pages and prevents orchestration from becoming procedural.
* **MAY**: Pages/Layouts import `Browser.Navigation` and `Url` only for routing/navigation glue; route params **MUST** be validated before use (especially if they become Domain identifiers).
* **MUST**: `Components/` should not perform app-level effects (no HTTP/ports)

  * If a component needs local state, it **MAY** have local `Msg`/`Model` for UI toggles (modal open, selected tab, etc.).
  * If a component needs an app-level effect, it **MUST** emit an `Intent` message upward to the parent Page.
  * **MUST**: Components with effects define an `Intent` ADT and expose `update : Msg -> Model -> (Model, Maybe Intent)` and `view : Model -> Html Msg`. Pages translate `Intent` → `Cmd Msg` via `Effect/*`.
  * Example: a form component does not call HTTP directly; it returns a `FormIntent` to the Page, which dispatches the effect.

### 6.2 Shared module discipline

* **MUST** keep `Shared/` small and purely functional.
* **MUST NOT** place JSON/HTTP/time/ports in `Shared/`.
* If a helper is only used by one feature, it **MUST** live in that feature directory, not `Shared/`.

---

## 7. State modeling standard (Elm idioms that are mandatory)

### 7.0 Remote and Error type standardization

To prevent drift across features, type definitions **MUST** be centralized:

* **MUST**: `Remote a` and shared error types live in `Shared/Remote.elm` or `Domain/Error.elm` (choose one per project and document in README).
* **MUST**: `ApiError` and `ValidationError` remain distinct types; mapping to user-facing messages happens at the view boundary via typed rendering functions.
* **MUST**: All features reuse the same `Remote` type; do not define variants per feature.

Rationale: Centralized error types prevent "slightly different Remote" per feature and ensure consistent error handling and messages across the app.

### 7.1 "No boolean soup" — mandatory Remote + ViewState split

State **MUST** be separated into two layers:

**Remote state** (async, external): modeled with a single ADT (Remote a or similar)

```elm
type Remote a
  = NotAsked
  | Loading
  | Failure Error
  | Success a
  | Refreshing a  -- optional: stale data while loading
```

**View state** (UI-only): boolean toggles, selected tabs, expanded menus, etc. — kept separate.

```elm
type alias Model =
  { user : Remote User
  , ui :
    { isModalOpen : Bool
    , selectedTab : Tab
    }
  }
```

**Rules:**

* **MUST** represent async and multi-phase state with ADTs, not multiple `Bool/Maybe` fields.
* **MUST NOT** mix loading flags, error strings, and success data into a single record.
* For "stale-while-revalidate" or refresh patterns, **MUST** make the state explicit: `Refreshing a` instead of `(Loading, Success a)`.
* UI toggles **MUST** be in a separate `ui` field, never mixed into domain state.

### 7.2 Errors are data (typed, not strings)

* **MUST** define domain error types (not store raw `String`).
* **MUST** separate internal error structure from user-facing messages via a rendering function.

Example:

```elm
type ApiError
  = NetworkError
  | BadStatus Int
  | DecodeError String

viewError : ApiError -> String
viewError err =
  case err of
    NetworkError -> "Network connection failed."
    BadStatus code -> "Server error (" ++ String.fromInt code ++ ")."
    DecodeError _ -> "Unexpected response format."
```

**Rules:**

* **MUST NOT** store only `String` as error state.
* **MUST** use a typed error ADT.
* User-facing messages **MUST** be derived via a rendering function, not stored as raw strings in the model.
* This allows typed error handling, testing, and localization without spreading strings.

### 7.3 Time, randomness, and configuration are boundaries

* **MUST** not call `Time.now` or random generators deep inside logic.
* **MUST** pass in time/randomness as inputs to pure functions or orchestrate via `Cmd`.

---

## 8. Update architecture conventions

### 8.1 Message discipline

* **MUST** keep messages grouped by subsystem when complexity grows:

```elm
type Msg
  = User UserMsg
  | Api ApiMsg
  | Ui UiMsg
```

Then handle with helper functions:

```elm
update msg model =
  case msg of
    User m -> updateUser m model
    Api m  -> updateApi m model
    Ui m   -> updateUi m model
```

* **SHOULD** avoid large single `case` blocks; refactor into helpers early.

### 8.2 Effects returned, not performed

* **MUST** keep update functions returning `( Model, Cmd Msg )`
* **MUST** express effects via wrapper functions (in `Effect/*`) where practical.

---

## 9. JSON decoding/encoding standard (DTO → Domain validation pipeline)

The correct Elm decoding pattern separates **wire shape** (JSON) from **domain shape** (invariants).

### 9.1 Decoder architecture: DTO → validation → Domain (with exception)

**Mandatory pipeline:**

1. **Api DTO** — mirrors the wire JSON shape; loose, minimal validation
2. **Api decoder** — decodes wire format into DTO; tests with valid/invalid/missing cases
3. **Domain validation** — pure function that converts DTO to Domain type via `Result ValidationError DomainType`

**Exception:** Direct Domain decoding is permitted **only when** all of:

* The JSON schema is owned by the same repository (internal, not from untrusted external API)
* The decoder enforces all Domain invariants
* The PR includes tests proving invariant enforcement

Otherwise, DTO → validation is mandatory to maintain the boundary between wire format and domain logic.

Example:

```elm
-- Api DTO (wire shape)
type alias UserDto =
  { id : String
  , name : String
  , email : String
  }

-- Api decoder
userDtoDecoder : Decoder UserDto
userDtoDecoder = ...

-- Domain type (invariants enforced)
type UserId = UserId String
type Email = Email String
type User = User { id : UserId, name : String, email : Email }

-- Domain validation
validateUser : UserDto -> Result ValidationError User
validateUser dto = ...
```

**Rules:**

* Decoders **MUST** decode into loose DTO types (not `Domain.*` directly).
* Decoders **MAY** do syntactic validation (non-empty, well-formed).
* Domain invariants (valid email format, UserId constraints, etc.) **MUST** be enforced in validation functions, not in decoders.
* This keeps decoders simple, testable, and separate from domain rules.

### 9.2 Decoder quality requirements

* **MUST** test decoders with:

  * at least one valid payload
  * at least one invalid payload
  * at least one "missing field / wrong type" payload
* **SHOULD** treat decode failures as typed errors (not raw strings).

---

## 10. Ports standard: versioned envelopes and typed dispatch

Ports are language boundaries; carelessness here causes silent corruption. Enforce strict discipline.

### 10.1 Port protocol (mandatory)

* **MUST** use a versioned envelope format to allow protocol evolution.
* **MUST** dispatch inbound messages via tag, not raw payload inspection.
* **MUST**: Unknown tag and decode failures **MUST** produce a typed `PortError` event that is surfaced in Model (e.g., `Failure` state) and optionally reported via a logging port if the project has observability infrastructure.
* **MUST**: Port decoding **MUST** never crash; decode failures are values, not exceptions.

Rationale: Port failures are production-silent corruption vectors. Typed errors make failures debuggable and observable.

Example envelope:

```elm
type alias Envelope =
  { v : Int              -- protocol version
  , tag : String         -- message type identifier
  , payload : Value      -- actual data
  }

type PortMessage
  = LocalStorageSet { key : String, value : String }
  | LocalStorageGet String
```

**Inbound (from JS):**

* Decode `Envelope` first
* Dispatch on `tag` to typed Elm message
* **MUST** handle unknown tags safely (log or ignore, not crash)

**Outbound (to JS):**

* All messages **MUST** be constructed via typed functions, never raw `Encode.object`
* Increment `v` if protocol changes; handle multiple versions during migration

### 10.2 Ports module rules

* **MUST** centralize all ports in one module (`Ports.elm` or `Effect/Ports.elm`)
* **MUST** export typed wrapper functions, not bare ports
* **MUST NOT** expose raw `Port.toJs` or `Port.fromJs` to the rest of the app
* All port decoding/encoding **MUST** happen in the Ports module

---

## 11. Build and automation contract (Elm Land)

Elm/Elm Land projects **MUST** provide the canonical targets/commands:

* `fmt` → `elm-format --yes src tests` (local) / `elm-format --validate src tests` (CI)
* `lint` → `elm-review` (or document N/A with justification)
* `test` → `elm-test`
* `build` → `elm-land build` or equivalent
* `check` → `fmt && lint && test && build` in sequence
* `precommit` → `check` plus clean working tree guard

Example Makefile:

```make
.PHONY: fmt lint test build check precommit

fmt:
 elm-format --yes src tests

lint:
 elm-review

test:
 elm-test

build:
 elm-land build

check: fmt lint test build
 @echo "✅ All checks passed"

precommit: 
 @test -z "$$(git status --porcelain)" || (echo "Working tree not clean"; exit 1)
 $(MAKE) check
```

---

## 12. Mandatory Elm idioms (merge-blocking where relevant)

Beyond architecture, Elm code quality relies on consistent idioms. These are non-negotiable:

### 12.1 Opaque types for invariants

* **MUST** use custom types + smart constructors for domain primitives with invariants.

Example:

```elm
module Domain.Email exposing (Email, mkEmail)

type Email = Email String

mkEmail : String -> Result ValidationError Email
mkEmail s =
  if String.contains "@" s && String.length s > 0
    then Ok (Email s)
    else Err InvalidEmail
```

**Rule:** No raw `String`/`Int` for email, UserId, Money, etc. in Domain state.

### 12.2 Avoid Debug.log and Debug.todo in production

* **MUST NOT** commit `Debug.log` or `Debug.todo` to main branches.
* **MUST** add `elm-review` rule to forbid these in CI.
* Tests and local debugging are fine; production code is not.

### 12.3 Data structure choice by semantics

* Use `List` for small ordered collections or when order matters.
* Use `Array` for indexed access or large collections.
* Use `Dict` when keys matter; avoid `List (Tuple k v)`.
* Use `Set` for membership testing; avoid `List a` for "contains" checks.

**Rule:** Avoid accidental O(n²) behavior by choosing the right structure.

### 12.4 Html/Css consistency

If using `elm-css` or `Html.Styled`, **MUST** be standardized across the codebase.
If using core `Html`, do not mix in `elm-css`.

**Rule:** One approach per project, enforced in review.

---

## 13. Merge-blocking PR checklist (Elm Land)

This checklist is enforceable at review time. Items marked **MUST** block merges unless justified in ADR/PR comment.

### A. Boundary integrity (merge-blocking)

1. **MUST**: Domain modules do not import `Http`, `Json.Decode`, `Json.Encode`, `Time`, `Random`, `Browser.*`, `Ports`, or `ElmLand.*`.
2. **MUST**: All external inputs (HTTP, ports, flags, route params) are **validated** before entering Domain state.
3. **MUST**: `Pages/` and `Layouts/` do not import `Http`, `Json.Decode`, `Json.Encode`, or `Ports` directly.
4. **MUST**: All boundary work (effects) is obtained via `Api/*` or `Effect/*` functions.

### B. State modeling (merge-blocking)

1. **MUST**: Multi-phase async state uses a `Remote a` ADT (or equivalent), not scattered `Bool/Maybe` fields.
2. **MUST**: UI state (modal open, selected tab, hover) is in a separate `ui` record, never mixed into domain state.
3. **MUST**: Errors are typed ADTs, never raw `String` error state.
4. **MUST**: Components with local state emit intents upward; they do not call app-level effects directly.

### C. Update architecture (merge-blocking)

1. **MUST**: `update` uses message discipline (sub-Msg types) when complexity grows; no god-msg case blocks.
2. **MUST**: Side effects are returned as `Cmd`, not performed inside helpers.

### D. JSON + Ports (merge-blocking)

1. **MUST**: Decoders are tested with valid + invalid + missing/wrong-type cases.
2. **MUST**: Decoding pipeline: wire DTO → validation → Domain type (not direct DOM decoding).
3. **MUST**: Port messages use versioned envelope format; no raw untyped blobs.

### E. Tooling + review (merge-blocking)

1. **MUST**: `elm-format --validate`, `elm-review`, `elm-test`, build all pass locally and in CI.
2. **MUST**: No `Debug.log`, `Debug.todo` in production code; caught by elm-review.
3. **MUST**: No formatting/refactor/behavior mixed in one commit. **SHOULD** use separate commits (or PRs) for "fmt-only / rename-only / behavior change." If mixing is unavoidable, the PR **MUST** justify why separation was impractical (pressure-release valve for reviewers).
4. **MUST**: Dependencies managed via CLI tools only (`elm install`, `elm-land add`). Hand-editing `elm.json` is prohibited.

---

## 14. When this standard can be relaxed (false positives)

The following are **not violations**, even if they superficially resemble forbidden patterns:

* **Tiny apps or prototypes** — if a page is <200 lines and single-concern, strict separation may be over-engineered.
* **One-page spikes** — temporary Elm code for a spike does not need full boundary discipline; must be refactored before merging to main.
* **Internal domain validation** — decoding a simple JSON config file is acceptable if the file is internal (not untrusted external data).
* **Local component state** — modals, dropdowns, form field focus **are** fine as local `Bool` in component, provided no app-level effects leak.
* **Navigation effects** — using `Browser.Navigation` in Pages is acceptable (it is a standard orchestration effect).

**Reviewer guidance:** If code lives at a boundary, has explicit intent, and isolates concerns cleanly, it is likely fine even if it resembles a frowned-upon pattern. When in doubt, ask in PR or ADR.

---

## 15. Final Elm rule

If the code:

* permits invalid states,
* hides effects in helper functions,
* lacks type safety at boundaries (ports, HTTP),
* violates module boundaries,
* mixes async state and UI state,
* or requires guesswork to understand,

then it **violates this standard**, even if it compiles.
