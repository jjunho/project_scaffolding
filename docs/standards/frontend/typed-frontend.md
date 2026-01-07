# Typed Frontend Constitution

**(Functional Core, Explicit Boundaries, Anti-OOP Translation)**

> This document defines the minimum acceptable standard for typed frontend systems.
> It exists to prevent imperative, OOP-style UI architectures from being mechanically translated into typed languages without gaining their benefits.

If frontend code "looks like React/Vue/Angular with types sprinkled on top", it violates this constitution.

---

## Scope and intent

Applies to:

* Single-page and multi-page frontends
* Typed UI systems with a compiler or static type checker
* Applications with network, storage, or JS/host interop

This constitution is **architecture-first**, not framework-specific.

It is distilled from:

* Elm language semantics and ecosystem constraints
* Rakuten's large-scale Elm experience (what worked / what broke)
* Functional core discipline from Haskell
* Typed frontend best practices across PureScript, ReasonML/Rescript, Scala.js, F#/Fable, and disciplined TypeScript systems

---

## 1. Fundamental rule (non-negotiable)

> **Frontend systems MUST be designed in terms of values, types, and transformations — not components as objects, mutable view models, or lifecycle-driven behavior.**

Any design that starts from:

* "What component owns this state?"
* "What lifecycle hook do we use?"
* "Where do we mutate the model?"

is already wrong.

---

## 1.1 Violation classes

Not all violations have equal urgency. Enforcement varies by severity:

1. **CRITICAL**: Permits invalid states, unsafe boundaries
   → Merge-blocking, CI fails
2. **SERIOUS**: Hidden effects, domain logic in views
   → Merge-blocking, human review required
3. **WARNING**: Large orchestration functions, missing abstractions
   → Documented tech debt, refactor deadline set

---

## 2. Functional core, imperative shell (mandatory)

### 2.1 Split the system explicitly [CRITICAL]

Every typed frontend **MUST** be structured as:

* **Functional Core**
  * Pure domain logic, invariants, transformations
  * No effects, no IO, no UI assumptions
  * Testable without rendering or network calls

* **Imperative Shell**
  * Orchestration, rendering, effects, integration with the host platform
  * Thin; delegates to functional core
  * Visible in module organization

This split **MUST be visible in the module structure**, not just conceptual.

---

## 3. Boundaries are first-class (central lesson from Elm + Rakuten)

### 3.1 Boundary definition

A **boundary** is any translation between:

* **untrusted external input**
  (network, storage, URL params, JS/host APIs, user input)
* **trusted internal values**
  (domain types, invariants, validated state)

Boundaries are **security and correctness choke points**.

---

### 3.2 Boundary rules (merge-blocking) [CRITICAL]

* **MUST** decode/parse external input into *intermediate representations* (DTOs, protocols).
* **MUST** validate before converting into domain values.
* **MUST NOT** allow raw external representations into the core domain.
* **MUST** centralize boundary code (no ad-hoc decoding in views/components).
* **MUST** use typed envelopes or protocols for all external interop.

This rule alone prevents most production frontend bugs.

---

## 4. Domain modeling: illegal states are impossible

### 4.1 Types encode reality, not convenience

* **MUST** encode domain rules in types, not comments or conventions.
* **MUST** prefer ADTs / tagged unions over boolean flags.
* **MUST NOT** encode state machines with combinations of booleans.

Bad (language-agnostic):

```
loading: boolean
error: string | null
data: Data | null
```

Good:

```
Remote<Data> =
  | NotAsked
  | Loading
  | Failure(Error)
  | Success(Data)
```

---

### 4.2 Domain ≠ UI ≠ transport

* **Domain state**: business facts, invariants, constraints
* **UI state**: selection, visibility, focus, layout, modal open/closed
* **Transport state**: JSON, URLs, storage formats, interop protocols

**MUST NOT** mix these layers.

Example violation:

```
// WRONG: Domain + UI + transport mingled
type User = {
  id: string              // transport
  name: string            // domain
  loading: boolean        // UI
  localEdits: any         // UI
}
```

Example correct separation:

```
// CORRECT: Three separate types
type UserId = UserId(string)     // domain
type UserDto = { id: string, ... } // transport
type UserView = { isEditing: boolean, selectedTab: Tab, ... } // UI
```

Example 2: Form validation state

Bad:

```
{
  email: string,
  emailError: string | null,
  isValidating: boolean,
  isSubmitting: boolean
}
// Allows: isValidating=true, isSubmitting=true (impossible)
```

Good:

```
type FormState =
  | Editing(email: string, validation: Validation)
  | Submitting(email: ValidEmail)
  | Submitted(result: Result)

type Validation =
  | NotValidated
  | Validating
  | Valid(email: ValidEmail)
  | Invalid(error: ValidationError)
```

This is a core Rakuten lesson.

---

## 5. Effects are explicit, never hidden

### 5.1 Effects are values, not behavior

* **MUST** represent effects as explicit values/messages/commands.
* **MUST NOT** perform effects inside helpers or domain logic.
* **MUST** keep effect orchestration at the boundary layer.

No "hidden fetch," no implicit globals, no magical context access.

Bad:

```
function calculateDiscount(user: User): number {
  const tier = fetchUserTier(user.id);  // HIDDEN EFFECT
  return tier.discount;
}
```

Good:

```
function calculateDiscount(userTier: Tier): number {
  return userTier.discount;  // pure
}
// Caller orchestrates: fetch tier, then call this function
```

---

### 5.2 Imperative sequencing is allowed only at the shell

* Sequencing (do X, then Y, then Z) is acceptable for **orchestration**.
* Sequencing is forbidden for modeling **logic**.

If logic requires step-by-step execution, the model is wrong.

The shell (main event loop, thunk middleware, command orchestration) is where sequencing lives.

### 5.3 Effect testing discipline

Tests **MUST** verify:

1. What effects were requested (as values)
2. How the system responds to effect results

Bad (untestable):

```
function handleLogin(username, password) {
  api.login(username, password)  // effect happens NOW
}
```

Good (testable):

```
function handleLogin(username, password): Effect {
  return { type: "ApiCall", endpoint: "login", data: {username, password} }
}

test("login emits correct API effect", () => {
  const effect = handleLogin("user", "pass")
  assert(effect.type === "ApiCall")
  assert(effect.endpoint === "login")
})
```

---

## 6. Update / orchestration discipline (TEA generalized)

### 6.1 Orchestration is not modeling

Message/update loops (Elm TEA, Redux, state machines) are:

* **Orchestration mechanisms**
* **Not domain models**

Rules:

* Core domain logic **MUST** live outside orchestration code.
* Orchestration code **MUST** delegate to pure functions.
* Large monolithic update handlers are a smell.

Example (Elm-like, applies to any typed language):

Bad:

```
update msg model =
  case msg of
    FetchUser id ->
      let (newData, cmd) = ... in
        ... complex domain logic directly in update ...
```

Good:

```
update msg model =
  case msg of
    FetchUser id ->
      let result = validateAndProcessUser model id in
        applyResult result model

validateAndProcessUser : Model -> UserId -> Result Error User =
  ... pure domain logic ...
```

Rakuten learned this the hard way.

---

### 6.2 Message discipline (anti-god-update)

* **MUST** group messages by subsystem when complexity grows.
* **MUST** refactor early; large switch/case blocks are merge-blocking.
* **MUST** keep orchestration readable, linear, and shallow.

Pattern:

```
type Msg
  = User UserMsg
  | Api ApiMsg
  | Ui UiMsg
  | Navigation NavMsg

update msg model = case msg of
  User m     -> updateUser m model
  Api m      -> updateApi m model
  Ui m       -> updateUi m model
  Navigation m -> updateNavigation m model
```

---

## 7. Errors are data, not strings or exceptions

* **MUST** represent errors as typed values (ADTs, enum variants, etc.).
* **MUST NOT** store raw strings as the sole error representation.
* **MUST** separate internal error structure from user-facing messages.

This enables:

* testing
* localization
* refactoring without hunting for strings
* observability (typed error reporting)

Example:

```
type ApiError
  = NetworkTimeout
  | BadStatus(Int)
  | DecodeError(String)
  | Unauthorized

userMessage : ApiError -> String
userMessage err = case err of
  NetworkTimeout -> "Connection lost. Please try again."
  BadStatus 401 -> "Your session expired. Please log in."
  ...

logError : ApiError -> Command
logError err = ...
```

---

## 8. Interop (JS / host APIs / storage) is a protocol

### 8.1 Interop is not a function call

Rakuten's most painful failures came from treating interop casually.

Rules:

* **MUST** treat interop as a **versioned protocol**.
* **MUST** use typed envelopes/messages (not raw blobs).
* **MUST** handle unknown/invalid messages safely (never crash).
* **MUST** centralize all interop in a single boundary module.
* **MUST** document the interop contract (version, message types, error handling).

Interop is equivalent to network IO, even if it's "local".

### 8.2 Interop versioning (mandatory)

All interop messages MUST include:

* Schema version identifier
* Explicit backwards compatibility policy

Bad:

```
sendToJS({ type: "UserLoggedIn", userId: "123" })
```

Good:

```
type InteropEnvelope<T> = {
  version: "v1" | "v2",
  payload: T
}

sendToJS({
  version: "v1",
  payload: { type: "UserLoggedIn", userId: "123" }
})
```

When receiving from JS:

* MUST parse version first
* MUST handle unknown versions gracefully (return error, don't crash)
* MUST NOT assume payload structure without validation

---

## 9. Component discipline (anti-object UI)

### 9.1 Components are not objects

* **MUST NOT** treat UI components as stateful objects with methods.
* **MAY** have **local UI state** (visibility, focus, selected tab).
* **MUST NOT** own domain state or perform global effects.

Example of acceptable local state:

```
type ComponentModel = {
  isModalOpen: boolean,
  selectedTab: Tab,
  hoverIndex: number | null,
  ...
}
// This is fine; it's pure presentation state.
```

Example of forbidden component behavior:

```
// WRONG: Component owns domain state or performs global effects
type ComponentModel = {
  users: User[],           // domain? no.
  loading: boolean,        // global async state? no.
  ...
}
component.fetchAndUpdate() // effect hidden in component
```

---

### 9.2 Acceptable component patterns

Components MAY:

* Accept typed props/inputs
* Emit typed events/outputs
* Manage local UI state (focus, hover, animation state)
* Derive display values from props

Components MUST NOT:

* Store or cache domain state
* Make API calls directly
* Subscribe to global stores directly (use passed-down props)
* Perform side effects beyond updating their own local UI state

When components need "intelligence":

* Extract to pure function returning view model
* Pass view model as prop

If component needs effect (HTTP, storage), use intent pattern:

```
type Intent = RequestDelete(Id)

update msg model = ... (Model, Maybe Intent)
```

Parent handles intent and performs effect.

Example: component requests delete, parent decides whether to call HTTP.

If a component needs an effect (HTTP, navigation, storage):

* It emits an **intent** message upward.
* The parent orchestrator decides what to do.
* The component never performs the effect directly.

Pattern:

```
type ComponentIntent
  = RequestDelete(Id)
  | RequestNavigation(Url)

componentView : ComponentModel -> Html ComponentMsg
componentUpdate : ComponentMsg -> ComponentModel -> (ComponentModel, Maybe ComponentIntent)

// Parent handles intents
parentUpdate msg model = case msg of
  ComponentMsg m ->
    let (newComp, intent) = Component.update m model.component in
    case intent of
      Just (ComponentIntent.RequestDelete id) ->
        (model, deleteUser id)  // Parent orchestrates effect
      ...
```

---

## 10. Data structures reflect semantics and complexity

**Rule**: Data structures **MUST** make complexity visible in their type signature.

### 10.1 Merge-blocking violations

* Using List<T> when cardinality constraints exist (min/max, uniqueness)
* Using Map<K,V> when key structure has semantic meaning
* Using optional fields when the optionality represents a state machine

### 10.2 Acceptable

* List<T> for genuinely unbounded collections with no ordering invariants
* Map<K,V> for truly key-value storage with arbitrary keys

---

## 11. Tooling is part of the architecture

* **MUST** enforce formatting, linting, testing, and build in CI.
* **MUST** treat compiler errors as merge-blocking.
* **MUST** forbid debug code (`console.log`, `Debug.log`, etc.) in production.
* **MUST** keep builds reproducible (pinned versions, lockfiles).

Rationale: Rakuten's success relied on compiler enforcement, not developer heroics.

---

## 12. Anti-patterns (hard stop)

The following indicate OOP/imperative leakage and must be refactored:

* **Boolean soups** for async state (loading + error + data = three separate booleans/nulls)
* **"God components"** or **"god update functions"** (>300 LOC, >20 message types, deep nesting)
* **Hidden effects** in helpers
* **Untyped interop blobs** (raw JSON values, raw port messages)
* **Domain logic inside views** (calculations, validation in render code)
* **Lifecycle-driven behavior** ("on mount, do X"; "on unmount, clean up Y")
* **State mutated "because the UI needs it"** (side effects in getters/helpers)
* **Components as stateful objects** (methods, internal mutation, effect-performing)

If these appear, refactor. Do not merge.

---

## 13. When rules may be relaxed (explicitly)

Allowed, with documentation:

* **Prototypes and spikes**: Full architecture not required; must be refactored before merging to main.
* **Tiny, single-screen apps**: <200 lines, single domain, no network = strict separation may be over-engineered.
* **Temporary glue code during migration**: Boundary violations acceptable during major refactors; must be tracked and resolved.
* **Local component state**: Boolean toggles, focus, selected tab in component are fine.

**Rule:** Anything merged to main must conform.

---

## 14. Incremental adoption strategy

When migrating existing codebases:

### Phase 1 (Foundation)

* **MUST** establish boundary layer for all external input

* **MAY** keep existing component structure temporarily

### Phase 2 (Core extraction)

* **MUST** extract pure domain logic from components

* **MUST** make implicit state machines explicit (Remote<T>, etc)

### Phase 3 (Effect discipline)

* **MUST** make effects explicit

* **MAY** use adapter layer to legacy effect systems

### Phase 4 (Full compliance)

* **MUST** refactor orchestration

* **MUST** enforce all constitutional rules

**Timeline**: Each phase MUST complete before next begins. Stalled migrations revert to Phase 1.

---

## 15. Performance as a constitutional concern

Functional purity **MUST NOT** be used as excuse for poor performance.

### Required

* Memoization strategy for expensive computations

* Explicit rendering optimization (when needed)
* Performance budgets in CI

### Forbidden

* "Premature optimization" as excuse for always-recompute

* Mutable escape hatches without documentation
* Performance fixes that violate boundaries

---

## 16. Enforcement mechanisms

### Required tooling:

1.  **Type system MUST catch boundary violations**
    * Static analysis only; no reliance on runtime checking for internal logic.

2.  **Linters MUST catch:**
    * Effects in pure functions (pattern matching on known effect types).
    * Domain logic in view files (enforce architectural boundaries).
    * Missing error handling at boundaries.

3.  **Tests MUST verify:**
    * All boundary codecs (round-trip property tests).
    * Domain invariants hold after updates.
    * Effects are values, not executed.

### 4. Code review checklist (human):

* "Does this change introduce implicit state?"
* "Are boundaries clearly marked?"
* "Can this fail at runtime in ways the types don't prevent?"

---

## Final constitutional rule

If frontend code:

* permits invalid states,
* hides effects,
* blurs boundaries,
* relies on runtime discipline instead of types,
* or could be mechanically rewritten in untyped JavaScript with little loss of correctness,

then it **violates this constitution**, regardless of framework or language.

---

## Appendix A: Minimal Example System

(Pseudocode demonstrating the layers)

```text
// 1. Domain (PURE, STRICT)
type User = Active(Name, Email) | Deleted(Id)
fn activate(u: User) -> Result<User, Error>

// 2. Boundary (UNTRUSTED inputs -> Domain)
fn deployUser(json: Unknown) -> Result<User, DecodeError> {
  dto = parse(json) // Fail hard here
  validate(dto)     // Convert to Domain
}

// 3. Effect (INTERFACE)
interface UserRepo {
  fn save(u: User) -> Future<Unit>
}

// 4. UI Orchestration (IMPERATIVE SHELL)
fn onRegisterClick(input: String) {
  match deployUser(input) {
    Ok(user) -> runEffect(repo.save(user))
    Err(e)   -> showToast(e)
  }
}
```

## Appendix B: TypeScript/JS Reality

For TypeScript projects adhering to this constitution:

*   **`any` is FORBIDDEN** except at the rawest IO boundary lines.
*   **`unknown` is PREFERRED** for external inputs until validated.
*   **Zod/io-ts (Runtime Validation)** is **MANDATORY** at boundaries. TypeScript types disappear at runtime; you must parse.

---

## Closing synthesis

* **Elm taught us** *what is possible* — a typed language can eliminate entire categories of runtime errors.
* **Rakuten taught us** *what breaks at scale* — discipline on boundaries, state separation, and message orchestration are non-negotiable.
* **Haskell taught us** *how to design the core correctly* — types as constraints, not decoration; purity as architecture.

This constitution encodes the shared lesson:

> **Typed frontends succeed only when types, boundaries, and purity are used as architectural constraints — not optional documentation.**

---

## See also

* [Universal Project Standard](STANDARD.md) — Language-agnostic baseline
* [Elm/Elm Land Language Addendum](elm.md) — Elm-specific instantiation of this constitution
* [Haskell Language Addendum](haskell.md) — Functional core design patterns
