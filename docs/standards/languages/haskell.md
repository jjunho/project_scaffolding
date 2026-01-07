# Haskell Language Addendum

**(Functional-first, Haskell-native, anti-OOP translation)**

> This document extends the Universal Project Standard for Haskell projects.
> It exists specifically to prevent object-oriented or imperative designs from being mechanically translated into Haskell syntax.

If code "looks like Java/Python with `do` notation", it violates this addendum.

---

## 1. Fundamental rule (non-negotiable)

> **Haskell code MUST be designed in terms of values, types, and transformations — not objects, methods, or mutable state.**

The goal is not to eliminate sequencing, mutation, or effects, but to **confine them** so that the domain remains algebraic, testable, and inevitable.

Any design that starts from:

* "What class should this be?"
* "What methods does this object have?"
* "What is the lifecycle of this object?"

is already wrong in Haskell.

---

### Scope: What is "boundary code"?

**Boundary code**: code whose sole purpose is to translate between the outside world and the domain (IO, HTTP, DB, CLI, config, time, randomness).

Boundary code **MAY** use `do` notation, `IO`, sequencing, and mutation as appropriate. The restriction applies only to domain logic, not orchestration at the edge.

### Architecture Layers

The system is stratified from pure to impure:

1.  **Domain** (`src/Domain/`): Pure business logic, types, errors. No `IO`, no exceptions.
2.  **Effect** (`src/Effect/`): Interfaces (typeclasses) for side effects.
3.  **Workflow** (`src/Workflow/`): Orchestrates Domain using Effects.
4.  **App** (`src/App/`): Concrete implementations of Effects, dependency injection, and Main entry point.

---

## 2. Domain modeling: ADTs, not classes

### 2.1 Algebraic Data Types are the primary modeling tool

* **MUST** model domain concepts using **ADTs**, not records-as-objects.
* **MUST** encode business rules in the type system.
* **MUST** make illegal states unrepresentable in closed, finite state spaces.

Exception: When the state space is externally defined, unbounded, or performance-critical, invariants **MAY** be enforced via smart constructors and validation functions rather than full ADT refactoring, provided:

* illegal states are rejected early and explicitly
* validation failures are typed (not stringly-typed)
* the rationale is documented in a comment or ADR

Bad (OOP-style record-as-object):

```haskell
data User = User
  { userId :: Int
  , name :: String
  , isActive :: Bool
  , isDeleted :: Bool
  }
```

Good (state encoded in the type):

```haskell
data User
  = ActiveUser UserId Name
  | DeletedUser UserId DeletedAt
```

Rule:

* **MUST NOT** use boolean flags or nullable fields to encode state machines.

---

### 2.2 Records are data, not behavior containers

* **MUST NOT** treat records as "objects with methods".
* **MUST** keep behavior as *functions over data*, not methods "attached" to data.

Bad (pseudo-method mindset):

```haskell
activateUser :: User -> User
activateUser u = u { isActive = True }
```

Good (explicit state transition):

```haskell
activate :: User -> Maybe User
activate (DeletedUser _ _) = Nothing
activate (ActiveUser _ _)  = Nothing
activate (InactiveUser i n) = Just (ActiveUser i n)
```

---

## 3. Functions, not procedures

### 3.1 Prefer expressions, not sequences

(Refer to existing text about do-notation avoidance)

### 3.2 Total Functions Only

- **MUST**: Functions must be total (defined for all inputs).
- **MUST NOT**: Use partial functions like `head`, `tail`, `!!`, or incomplete pattern matches in production code.
- **Exception**: Partial functions are **ALLOWED** only in tests or branches provably unreachable (with comments).

---

## 4. Performance Philosophy

1. **Correctness First**: Optimize only after correctness is proven.
2. **Measure First**: No optimization without a benchmark.
3. **Explicit Strictness**: Use strict data fields by default (`data User = User !Int !Text`) to avoid space leaks, unless laziness is required for control flow.

---

* **MUST** prefer expression-oriented code.
* **MUST** avoid long `do` blocks that simulate imperative flow **in domain logic**.
* **MAY** use `do` notation for effect orchestration and boundary code where sequencing is semantically meaningful.

Bad (pure logic in `do`):

```haskell
process :: Input -> IO Output
process input = do
  a <- stepA input
  b <- stepB a
  c <- stepC b
  pure c
```

Good (effect orchestration at boundary):

```haskell
handler :: Request -> IO Response
handler req = do
  input <- decode req
  result <- process input
  respondOk result
```

Good (pure pipeline):

```haskell
process :: Input -> Output
process =
  stepC
  . stepB
  . stepA
```

Rule:

* **MUST** default to composition (`.` / `>=>`) for pure transformations.
* **MUST NOT** use `do` to express pure computations or domain logic.
* **MAY** use `do` to orchestrate effects at boundaries.

---

### 3.2 `do` notation is for *effects*, not logic

* **MUST NOT** use `do` blocks for pure logic.
* **MUST** refactor logic into pure helpers outside `do`.

Bad:

```haskell
do
  let x = f a
  let y = g x
  let z = h y
  pure z
```

Good:

```haskell
pure $ h $ g $ f a
```

or better:

```haskell
h . g . f $ a
```

---

## 4. Effects: model, don't hide

### 4.1 Effects are explicit in types

* **MUST** express effects in the type signature.
* **MUST NOT** hide effects behind polymorphism or implicit globals.
* **MUST** prefer *effect algebras* over concrete monads in core logic.

Bad (concrete IO everywhere):

```haskell
loadUser :: UserId -> IO User
```

Good (effect abstracted):

```haskell
loadUser :: MonadUserRepo m => UserId -> m User
```

or explicitly:

```haskell
loadUser :: UserId -> AppM User
```

with `AppM` documented as the *composition* of effects, not a "God monad".

---

### 4.2 Avoid the "God monad" anti-pattern

* **MUST NOT** create monads that act as implicit service locators.
* **MUST** document what effects exist and why.

Bad:

```haskell
newtype App a = App { runApp :: ReaderT Env IO a }
```

with `Env` containing everything.

Better:

```haskell
data Env = Env
  { userRepo :: UserRepo
  , clock    :: Clock
  }
```

Best (when complexity grows):

* Explicit effect algebras
* Small capability typeclasses
* Or explicit effect records passed as arguments

---

## 5. Typeclasses: laws first, not interfaces

### 5.1 Typeclasses are not interfaces

* **MUST NOT** use typeclasses as "interfaces with methods" in the OOP sense.
* **MUST** use typeclasses only when:

  * there are **laws**
  * multiple meaningful instances exist
  * ad-hoc polymorphism is required

* **SHOULD** encourage typeclasses when they express an **algebra with laws** (e.g., `Foldable`, `Traversable`, domain-specific algebras).

Bad (Java interface in disguise):

```haskell
class UserService a where
  createUser :: a -> User -> IO ()
```

Good (capability with laws or minimal surface):

```haskell
class Monad m => MonadUserRepo m where
  insertUser :: User -> m ()
```

Good (lawful algebra):

```haskell
class Foldable f where
  foldr :: (a -> b -> b) -> b -> f a -> b
```

Even better:

* Keep typeclasses *small*
* Prefer records-of-functions when no laws exist
* Document why lawfulness matters

---

### 5.2 Respect algebraic laws

* **MUST** respect and document laws for:

  * `Functor`
  * `Applicative`
  * `Monad`
  * `Semigroup` / `Monoid`
* **MUST NOT** write instances that violate laws for convenience.

---

## 6. Data flow over control flow

### 6.1 Use folds, maps, and recursion schemes

* **MUST** prefer `map`, `foldr`, `foldl'`, `traverse`, `sequence` over explicit loops.
* **MUST** avoid index-based logic.

Bad:

```haskell
process xs = go 0 xs
```

Good:

```haskell
process = foldl' step initial
```

or:

```haskell
process = traverse transform
```

---

### 6.2 Model pipelines, not workflows

OOP mindset:

> "First do this, then that, then update state."

Haskell mindset:

> "Transform values through a pipeline; effects decorate the edges."

Rule:

* **MUST** think in *data transformation graphs*, not execution steps.

---

## 7. Error handling: values, not exceptions

* **MUST** prefer `Either`, `Maybe`, or domain-specific error ADTs.
* **MUST NOT** throw exceptions for domain errors.
* **MUST** pattern match exhaustively.

Bad:

```haskell
error "invalid state"
```

Good:

```haskell
data ValidationError
  = EmptyName
  | InvalidEmail
```

---

## 8. Naming and structure (Haskell idioms)

* **MUST** name functions as verbs or transformations.
* **MUST** name types as nouns.
* **SHOULD** avoid `get`, `set`, `update` unless semantically precise.
* **MUST** organize modules by **concept**, not by "layered OOP architecture".

Bad module naming:

* `UserService`
* `UserManager`
* `UserController`

Good:

* `Domain.User`
* `User.Validation`
* `User.Repository`
* `User.Workflow`

---

## 9. When you see these, stop and refactor

The following are **red flags** indicating OOP-thinking leakage:

* Large records with many fields + many "update" functions
* Long `do` blocks doing pure logic
* Typeclasses with many unrelated methods
* Boolean flags encoding state
* `IO` in core business logic
* "Manager", "Service", "Controller" modules
* Comments explaining *how* instead of types enforcing *what*

---

## 10. Refactoring catalogue: Common OOP→Haskell translation mistakes

The following are the 10 most common failure modes in code that looks syntactically valid but is fundamentally OOP-thinking in Haskell clothes. Each includes the symptom, why it fails, and the idiomatic refactor.

### 10.1 Records-as-objects ("fat record + many update functions")

**Symptom:**

* Large record types with many fields
* Many functions of shape `foo :: X -> X` that mutate fields via record update
* State encoded via `Bool` flags and `Maybe` placeholders

Bad:

```haskell
data User = User
  { userId    :: UserId
  , name      :: Text
  , isActive  :: Bool
  , deletedAt :: Maybe UTCTime
  }

activate :: User -> User
activate u = u { isActive = True }
```

**Why it violates Haskell thinking:**

* "State machine as booleans" allows illegal combinations (`isActive=True` + `deletedAt=Just ...`).
* Transitions become runtime conventions, not enforced by types.

**Refactor pattern:** ADT encodes states; transitions become total or explicitly partial.

Good:

```haskell
data User
  = Inactive UserId Name
  | Active   UserId Name
  | Deleted  UserId DeletedAt

activate :: User -> Either DomainError User
activate (Inactive i n) = Right (Active i n)
activate (Active _ _)   = Left AlreadyActive
activate (Deleted _ _)  = Left AlreadyDeleted
```

**Normative rule:** Domain state machines **MUST** be modeled with ADTs, not boolean soups.

---

### 10.2 "Service / Manager / Controller" modules

**Symptom:**

* Modules named `*Service`, `*Manager`, `*Controller`
* Functions are long "workflows" with lots of `IO`, logging, branching, and mutation-like sequencing

Bad:

```haskell
createUserController :: Env -> Request -> IO Response
createUserController env req = do
  body <- readBody req
  user <- parse body
  ok   <- userServiceCreate env user
  if ok then pure success else pure failure
```

**Why it violates Haskell thinking:**

* Collapses domain logic + validation + effects into procedural orchestration.
* Prevents reuse and law-driven testing.

**Refactor pattern:** Split into (a) pure domain, (b) boundary decoding/encoding, (c) effectful orchestration thin layer.

Good module shape:

* `Domain.User` (types + pure rules)
* `User.Validation` (pure validation)
* `User.Workflow` (minimal, effect-polymorphic)
* `Web.UserRoutes` (HTTP glue only)

Good workflow core:

```haskell
createUser :: MonadUserRepo m => CreateUserInput -> m (Either DomainError UserId)
createUser input =
  pure (validate input)
  >>= traverse insertValidatedUser
```

**Normative rule:** "Controller/service" layers **MUST** be decomposed into pure domain + thin boundaries.

---

### 10.3 Long `do` blocks used for pure logic

**Symptom:**

* Many `let` bindings in `do`
* Control-flow heavy code mimicking imperative step-by-step logic

Bad:

```haskell
compute :: Int -> Int -> Int
compute a b = runIdentity $ do
  let x = a + 1
  let y = x * 2
  let z = y - b
  pure z
```

**Refactor pattern:** Use composition/pipelines as expressions.

Good:

```haskell
compute :: Int -> Int -> Int
compute a b =
  (\x -> x - b)
  . (* 2)
  . (+ 1)
  $ a
```

**Normative rule:** `do` notation **MUST NOT** be used for pure computations.

---

### 10.4 Nested `if`/`case` ladders instead of modeling decisions

**Symptom:**

* "Decision logic" encoded as nested branches
* Many runtime checks for impossible states

Bad:

```haskell
price :: Order -> Money
price o =
  if isCancelled o then 0
  else if isDiscounted o then subtotal o - discount o
  else subtotal o
```

**Refactor pattern:** Represent the decision space in the type; compute by pattern matching.

Good:

```haskell
data Order
  = Cancelled
  | Regular Subtotal
  | Discounted Subtotal Discount

price :: Order -> Money
price Cancelled           = 0
price (Regular s)         = s
price (Discounted s disc) = s - disc
```

**Normative rule:** Branch-heavy logic **SHOULD** become pattern matching over ADTs.

---

### 10.5 Exceptions used for domain errors

**Symptom:**

* `error`, `throwIO`, `Exception` for predictable failures
* "Validation failure" represented as crash or thrown exception

Bad:

```haskell
parseAge :: Text -> IO Int
parseAge t =
  case readMaybe (toString t) of
    Nothing -> throwIO (userError "bad age")
    Just a  -> pure a
```

**Refactor pattern:** Domain errors are values (`Either`); thrown exceptions reserved for unrecoverable failures.

Good:

```haskell
data ParseError = BadAge

parseAge :: Text -> Either ParseError Int
parseAge t =
  maybe (Left BadAge) Right (readMaybe (toString t))
```

**Normative rule:** Domain errors **MUST** be values (`Either`/ADT), not exceptions.

---

### 10.6 "Interface typeclasses" with many unrelated methods

**Symptom:**

* Typeclass used like Java interface
* Many methods bundled into one typeclass; no laws

Bad:

```haskell
class UserService m where
  create :: User -> m UserId
  delete :: UserId -> m ()
  list   :: m [User]
  audit  :: m [AuditLog]
```

**Refactor patterns:**

A) Split into small capability typeclasses, each with coherent purpose
B) Use record-of-functions when no laws / no need for ad-hoc polymorphism

Good (capabilities):

```haskell
class Monad m => MonadUserRepo m where
  insertUser :: User -> m UserId
  deleteUser :: UserId -> m ()

class Monad m => MonadAudit m where
  recordEvent :: AuditEvent -> m ()
```

Good (record-of-functions):

```haskell
data UserRepo m = UserRepo
  { insertUser :: User -> m UserId
  , deleteUser :: UserId -> m ()
  }
```

**Normative rule:** Typeclasses **MUST NOT** be used as "god interfaces". Prefer small capabilities or records.

---

### 10.7 Passing "Env" everywhere (service locator)

**Symptom:**

* A large `Env` record containing everything
* Most functions accept `Env -> ...`

Bad:

```haskell
data Env = Env { db :: Db, logger :: Logger, cfg :: Config, ... }

foo :: Env -> Input -> IO Output
foo env x = ...
```

**Refactor patterns:**

* In core logic: pass only what is needed (explicit dependencies)
* For effects: use capabilities or `ReaderT` but keep environment minimal and structured by boundary

Good:

```haskell
data Env = Env
  { userRepo :: UserRepo AppM
  , clock    :: Clock AppM
  }
```

**Normative rule:** "Env as service locator" **MUST** be minimized; core functions must not depend on the whole world.

---

### 10.8 Mutable-state thinking inside ST/IORef as default

**Symptom:**

* Defaulting to `IORef`, `MVar`, `TVar` even when unnecessary
* Algorithm written "like imperative" with local mutation

**Refactor pattern:**

* Use pure transformations first
* Use `foldl'`, strict data structures, and persistent updates
* Introduce mutation only if proven necessary and isolated

**Normative rule:** Local mutation **MAY** be used for performance, but only after measurement and must be isolated behind a pure interface.

---

### 10.9 Overusing `Monad` where `Applicative`/`Traversable` fits

**Symptom:**

* Everything written with `>>=` even when independent
* Missed parallelism/clarity opportunities

Bad:

```haskell
mk :: Monad m => m A -> m B -> m (A, B)
mk ma mb = do
  a <- ma
  b <- mb
  pure (a, b)
```

Good:

```haskell
mk :: Applicative m => m A -> m B -> m (A, B)
mk = liftA2 (,)
```

**Normative rule:** Use the weakest abstraction that works (`Functor`/`Applicative` over `Monad`).

---

### 10.10 Lists used when richer structures fit (and performance suffers)

**Symptom:**

* `[]` used for everything: sets, maps, keyed collections
* O(n²) behavior "by accident"

**Refactor pattern:**

* Use `Map`, `HashMap`, `Set`, `Vector` where semantically appropriate
* Make complexity visible by choosing the right type

**Normative rule:** Data structures **MUST** reflect semantics and complexity requirements.

---

## 11. Mandatory idioms checklist for PR review (merge-blocking)

This is a reviewer-grade checklist. Items marked **MUST** are merge-blocking unless an exception is documented (ADR/PR justification with scope and expiry). Items marked **SHOULD** are strong recommendations; exceptions require rationale.

### 11.A "Not an OOP translation" gate (hard stop)

1. **MUST**: The design is expressed as **types + functions over values**, not "objects with methods".
   Red flags (merge-blocking unless justified):

   * "Service/Manager/Controller" modules that own business logic
   * large "record + update methods" patterns
   * control-flow-heavy code that reads like Java/Python

2. **MUST**: Core domain logic is **pure** and testable without `IO`.

   * `IO` at the boundary is acceptable; `IO` in domain logic is not.

3. **MUST**: Business rules are not encoded as booleans and nullable fields.

   * Replace boolean soups with ADTs.

---

### 11.B Domain modeling (types are the primary artifact)

4. **MUST**: Illegal states are unrepresentable (or at least aggressively minimized).
   Checklist:

   * state machines modeled with ADTs
   * invariants enforced by constructors/smart constructors
   * forbidden combinations eliminated by design

5. **MUST**: Newtypes for domain primitives where ambiguity exists.
   Examples:

   * `newtype UserId = UserId UUID`
   * `newtype Email = Email Text`
   * `newtype Money = Money Scientific`
   
   No raw `Text`/`Int` for domain identifiers.

6. **SHOULD**: Separate validated from unvalidated data.
   Pattern:

   * `UnvalidatedX` / `ValidatedX` or `XRaw` / `X`
   * validation produces typed outcomes (`Either ValidationError X`)

---

### 11.C Effects and architecture (boundaries are explicit)

7. **MUST**: Side effects are isolated to boundary layers.

   * Domain modules must not import `IO` concerns (DB, HTTP, time, randomness, environment lookups).

8. **MUST**: Effects are explicit in types.

   * If a function reads time, it accepts time or runs in a clearly specified effect context.

9. **MUST**: No "God monad / service locator" by default.
   Merge-blocking indicators:

   * `ReaderT Env IO` with a large `Env` holding everything
   * ubiquitous `MonadReader Env m` constraints for domain code

   Acceptable patterns:

   * small capability typeclasses (cohesive responsibilities)
   * records-of-functions passed explicitly
   * a well-documented `AppM` with a minimal, intentionally scoped environment

10. **SHOULD**: Use the weakest abstraction that works.

    * prefer `Functor`/`Applicative` over `Monad`
    * prefer `traverse`/`sequenceA` over manual `do` loops

---

### 11.D Composition-first style (avoid imperative sequencing)

11. **MUST**: Pure logic is expressed as expressions and compositions, not `do` blocks.
    Merge-blocking:

    * `do` used for pure transformations
    * nested `case` ladders that should be ADTs

12. **SHOULD**: Pipelines and combinators are preferred over nested parentheses and deep nesting.
    Acceptable:

    * `($)` and composition (`.`) used to reduce noise
    * helper functions used to flatten indentation

13. **MUST**: Recursion and loops are expressed via folds, maps, and traversals unless recursion is genuinely clearer.

    * prefer `foldl'` for strict accumulation
    * prefer `Map`/`Set`/`Vector` when semantics demand it

---

### 11.E Error handling and totality

14. **MUST**: Domain errors are values (`Either`, `Maybe`, domain ADTs), not exceptions.
    Merge-blocking:

    * `error`, `undefined`, partial pattern matches in production paths
    * using `Exception` for expected domain failures

15. **MUST**: Pattern matches are total (or explicitly handled).

    * Use exhaustive matching; if impossible, prove it via types.

16. **SHOULD**: Use typed error structures with actionable context.

    * error ADTs carry enough detail to diagnose without leaking secrets

---

### 11.F Laziness, strictness, and performance correctness

17. **MUST**: Strictness is intentional where it matters.
    Merge-blocking indicators:

    * `foldl` used for large lists where `foldl'` is required
    * accumulating thunks in hot paths without justification

18. **SHOULD**: Choose data structures intentionally (semantics + complexity).

    * avoid "list everywhere"
    * prefer `Text` over `String` for non-trivial text handling

19. **MUST**: Optimization changes are measured and documented.

    * include benchmark/measurement notes if performance is claimed

---

### 11.G Typeclasses and instances (laws, coherence, minimality)

20. **MUST**: Typeclasses are not used as OOP interfaces.
    Merge-blocking:

    * large "service" typeclasses with unrelated methods
    * ad-hoc polymorphism without a real need

21. **MUST**: Instances respect laws (Functor/Applicative/Monad/Semigroup/Monoid).

    * If an instance is non-obvious, tests or rationale must exist.

22. **SHOULD**: Prefer `newtype`-deriving and lawful derivations (`DerivingVia` where appropriate) instead of hand-rolled instances.

---

### 11.H Module organization and naming

23. **MUST**: Module names reflect concepts, not "layers" borrowed from OOP.
    Avoid:

    * `*Controller`, `*Service`, `*Manager`
    
    Prefer:

    * `Domain.*`, `Workflow.*`, `Adapter.*`, `Persistence.*`, `Api.*`

24. **MUST**: No "Utils dumping ground."

    * helpers belong next to the concept they serve

25. **SHOULD**: Export lists are explicit in non-trivial modules.

    * avoid "expose everything" by default

---

### 11.I Tests and properties

26. **MUST**: New features include tests for happy path + primary failures.
27. **MUST**: Bug fixes include regression tests.
28. **SHOULD**: Invariants use property tests (QuickCheck/Hedgehog) when appropriate.
29. **MUST**: Tests are deterministic; flakiness is not acceptable.

---

### 11.J Tooling gate (universal contract, Haskell edition)

30. **MUST**: `fmt`, `lint`, `test`, `build`, `check` pass locally and in CI.
31. **MUST**: build is warning-free (warnings-as-errors where feasible).
32. **MUST**: no generated artifacts committed beyond `.gitignore`.

---

### Reviewer decision rule (simple and strict)

A PR is approvable only if:

* domain rules are expressed in types,
* effects are pushed to boundaries,
* errors are values,
* composition beats sequencing,
* and nothing resembles an OOP architecture translated into Haskell.

---

## 12. Things that are NOT violations (false positives)

The following patterns are **acceptable** and **not** violations of this standard, even though they may superficially resemble the antipatterns described above:

* **`do` notation in HTTP handlers, CLI parsers, or DB adapters** — these are boundary code; sequencing is appropriate.
* **Simple records used as DTOs or value objects** — these are not "objects with methods"; they are data containers.
* **`ReaderT` at the very edge of the system** — reading configuration or capabilities at the boundary is not a "god monad" if the environment is minimal and intentional.
* **Local mutation in tight loops with measurement and documentation** — pure solutions may be slower; document the tradeoff.
* **Partial pattern matches in tests** — tests may use `error` for invariant violations that should never occur.
* **External data validated via smart constructors** — not all data fits neatly into ADTs; typed validation functions are sufficient.
* **Temporary "Service" modules during refactoring** — provided they are marked as scaffolding and scheduled for decomposition.

**Reviewer guidance:** If code lives at a boundary, has explicit intent, and separates concerns, it is likely fine even if it resembles a frowned-upon pattern.

---

## 13. Final Haskell rule

If the Haskell code:

* mirrors OOP class diagrams,
* relies on sequencing instead of composition **in domain logic**,
* hides domain rules in runtime checks,
* uses monads as objects-with-methods,
* or could be mechanically rewritten in Java with minimal loss,

then it **violates this standard**, even if it compiles and passes tests.

---

## 14. Canonical Haskell project skeleton (Domain / Effect / App) with examples

This is a minimal, idiomatic, "Haskell-first" skeleton designed to prevent OOP-by-translation. It separates:

* `Domain/*` for pure types + rules (no IO)
* `Effect/*` for boundaries/capabilities (repo, clock, logging)
* `Workflow/*` for orchestration over capabilities (still testable)
* `App/*` for concrete wiring (IO, DB, HTTP, etc.)
* `Main` as entrypoint

This pattern uses "capabilities + AppM" which is explicit and avoids a "god interface". It also supports replacing capabilities with pure test interpreters.

### 14.1 Directory layout

```
.
├── README.md
├── CHANGELOG.md
├── Makefile
├── package.yaml        (or .cabal)
├── stack.yaml          (or cabal.project)
├── src/
│   ├── Domain/
│   │   ├── User.hs
│   │   ├── Email.hs
│   │   └── Error.hs
│   ├── Workflow/
│   │   └── CreateUser.hs
│   ├── Effect/
│   │   ├── UserRepo.hs
│   │   ├── Clock.hs
│   │   └── Log.hs
│   ├── App/
│   │   ├── Env.hs
│   │   ├── Monad.hs
│   │   └── UserRepoSql.hs     (example interpreter)
│   └── Main.hs
└── test/
    ├── Domain/
    │   └── EmailSpec.hs
    └── Workflow/
        └── CreateUserSpec.hs
```

Rules:

* `Domain` never imports `IO`, DB libs, HTTP libs, time acquisition, randomness, etc.
* `Workflow` depends only on `Domain` and `Effect` capabilities, never concrete infra.
* `App` is the only place where you talk to the world.

---

### 14.2 Domain layer (pure)

#### `src/Domain/Error.hs`

```haskell
module Domain.Error
  ( DomainError(..)
  , ValidationError(..)
  ) where

data ValidationError
  = EmptyName
  | InvalidEmail
  deriving stock (Eq, Show)

data DomainError
  = ValidationFailed ValidationError
  | UserAlreadyExists
  deriving stock (Eq, Show)
```

#### `src/Domain/Email.hs`

```haskell
module Domain.Email
  ( Email
  , mkEmail
  , unEmail
  ) where

import Data.Text (Text)
import qualified Data.Text as T
import Domain.Error (ValidationError(..))

newtype Email = Email { unEmail :: Text }
  deriving stock (Eq, Show)

mkEmail :: Text -> Either ValidationError Email
mkEmail t =
  let s = T.strip t
  in if isValid s
       then Right (Email s)
       else Left InvalidEmail

isValid :: Text -> Bool
isValid s =
  T.any (== '@') s
  && T.length s >= 3
```

This is intentionally simple; the key is the shape: validate at construction time, do not pass raw `Text` as "email".

#### `src/Domain/User.hs`

```haskell
module Domain.User
  ( UserId(..)
  , User(..)
  , NewUser(..)
  , mkNewUser
  ) where

import Data.Text (Text)
import Domain.Email (Email, mkEmail)
import Domain.Error (ValidationError(..))

newtype UserId = UserId { unUserId :: Text }
  deriving stock (Eq, Show)

data User = User
  { userId :: UserId
  , name   :: Text
  , email  :: Email
  } deriving stock (Eq, Show)

data NewUser = NewUser
  { newName  :: Text
  , newEmail :: Email
  } deriving stock (Eq, Show)

mkNewUser :: Text -> Text -> Either ValidationError NewUser
mkNewUser nameRaw emailRaw =
  case validateName nameRaw of
    Left e -> Left e
    Right nameOk ->
      mkEmail emailRaw
        >>= \emailOk ->
          Right NewUser
            { newName = nameOk
            , newEmail = emailOk
            }

validateName :: Text -> Either ValidationError Text
validateName t =
  let s = t
  in if s == "" then Left EmptyName else Right s
```

This prevents the classic OOP-translation problem where "User is a mutable bag of fields + setters".

---

### 14.3 Effect layer (capabilities, still not concrete)

These modules define *what* the app can do at the boundary, not *how*.

#### `src/Effect/UserRepo.hs`

```haskell
module Effect.UserRepo
  ( MonadUserRepo(..)
  ) where

import Domain.User (User, UserId, NewUser)

class Monad m => MonadUserRepo m where
  userExistsByEmail :: NewUser -> m Bool
  insertUser :: NewUser -> m UserId
  getUser :: UserId -> m (Maybe User)
```

Rule of thumb: keep capability typeclasses small and cohesive. If it grows, split it.

#### `src/Effect/Clock.hs`

```haskell
module Effect.Clock
  ( MonadClock(..)
  ) where

import Data.Time (UTCTime)

class Monad m => MonadClock m where
  now :: m UTCTime
```

#### `src/Effect/Log.hs`

```haskell
module Effect.Log
  ( MonadLog(..)
  , LogLevel(..)
  ) where

import Data.Text (Text)

data LogLevel = Debug | Info | Warn | Error
  deriving stock (Eq, Show)

class Monad m => MonadLog m where
  logMsg :: LogLevel -> Text -> m ()
```

---

### 14.4 Workflow layer (orchestration over capabilities)

Workflow is "business use-case code": minimal effects, maximal testability.

#### `src/Workflow/CreateUser.hs`

```haskell
module Workflow.CreateUser
  ( CreateUserInput(..)
  , createUser
  ) where

import Data.Text (Text)
import Domain.Error (DomainError(..), ValidationError(..))
import Domain.User (NewUser, UserId, mkNewUser)
import Effect.Log (MonadLog(..), LogLevel(..))
import Effect.UserRepo (MonadUserRepo(..))

data CreateUserInput = CreateUserInput
  { inputEmail :: Text,
    inputName :: Text
  }
  deriving stock (Eq, Show)

createUser ::
  (MonadUserRepo m, MonadLog m) =>
  CreateUserInput ->
  m (Either DomainError UserId)
createUser input =
  case mkNewUser input.inputName input.inputEmail of
    Left ve -> pure $ Left $ ValidationFailed ve
    Right newUser ->
      userExistsByEmail newUser >>= \exists ->
        if exists
          then pure $ Left UserAlreadyExists
          else
            insertUser newUser >>= \uid ->
              logMsg Info "User created" >> pure (Right uid)
```

This is deliberately explicit and still avoids OOP patterns:

* validation is pure and early
* repo access is a capability
* logging is a capability
* errors are values

If you want to reduce indentation further, you can refactor with small helpers, but this remains readable and law-abiding.

---

### 14.5 App layer (wiring + concrete interpreters)

#### `src/App/Env.hs`

```haskell
module App.Env
  ( Env(..)
  ) where

import Effect.Log (LogLevel(..))
import Domain.User (NewUser, UserId, User)

data Env m = Env
  { envGetUser :: UserId -> m (Maybe User),
    envInsertUser :: NewUser -> m UserId,
    envLog :: LogLevel -> String -> m (),
    envUserExistsByEmail :: NewUser -> m Bool
  }
```

**Note on Env growth:** If `Env` exceeds ~5 cohesive fields or mixes unrelated concerns (e.g., user repo + logging + metrics + config), it **MUST** be split into multiple environments or capabilities passed directly. This prevents the "god Env" antipattern.

#### `src/App/Monad.hs`

```haskell
module App.Monad
  ( AppM(..)
  , runAppM
  ) where

import Control.Monad.Reader (ReaderT(..), MonadReader(..))
import App.Env (Env(..))
import Effect.UserRepo (MonadUserRepo(..))
import Effect.Log (MonadLog(..))
import Effect.Log (LogLevel(..))
import qualified Data.Text as T

newtype AppM a = AppM { unAppM :: ReaderT (Env AppM) IO a }
  deriving newtype (Functor, Applicative, Monad)

runAppM :: Env AppM -> AppM a -> IO a
runAppM env (AppM r) = runReaderT r env

instance MonadUserRepo AppM where
  userExistsByEmail u = ask >>= \env -> env.envUserExistsByEmail u
  insertUser u = ask >>= \env -> env.envInsertUser u
  getUser uid = ask >>= \env -> env.envGetUser uid

instance MonadLog AppM where
  logMsg level msg =
    ask >>= \env -> env.envLog level (T.unpack msg)
```

This is explicit and keeps your constraints local. If Env grows, split the capabilities rather than growing a god-service.

#### Example interpreter stub: `src/App/UserRepoSql.hs`

```haskell
module App.UserRepoSql
  ( mkUserRepoSql
  ) where

import App.Env (Env(..))
import Domain.User (NewUser, UserId(..), User)
import Effect.Log (LogLevel(..))

mkUserRepoSql :: Env m -> Env m
mkUserRepoSql env =
  env
    { envGetUser = \_ -> pure Nothing,
      envInsertUser = \_ -> pure (UserId "generated-id"),
      envLog = \_ _ -> pure (),
      envUserExistsByEmail = \_ -> pure False
    }
```

This is intentionally a stub; in real code, this module would close over a DB pool/connection and implement the functions.

---

### 14.6 Entry point

#### `src/Main.hs`

```haskell
module Main (main) where

import App.Env (Env(..))
import App.Monad (AppM, runAppM)
import Workflow.CreateUser (CreateUserInput(..), createUser)

main :: IO ()
main =
  let env =
        Env
          { envGetUser = \_ -> pure Nothing,
            envInsertUser = \_ -> pure (error "wire real repo"),
            envLog = \_ _ -> pure (),
            envUserExistsByEmail = \_ -> pure False
          }
   in runAppM env $
        createUser (CreateUserInput "alice@example.com" "Alice")
          >>= \res ->
            case res of
              Left _ -> pure ()
              Right _ -> pure ()
```

For a real app, `Main` would parse config, build DB pools, and then run HTTP/CLI handlers. The core pattern remains: pure domain + capability-driven workflows.

---

### 14.7 Tests (examples)

#### `test/Domain/EmailSpec.hs` (Hspec example)

```haskell
module Domain.EmailSpec (spec) where

import Test.Hspec
import Domain.Email (mkEmail)

spec :: Spec
spec =
  describe "mkEmail" $ do
    it "accepts a valid email" $
      mkEmail "a@b" `shouldSatisfy` either (const False) (const True)

    it "rejects an invalid email" $
      mkEmail "abc" `shouldSatisfy` either (const True) (const False)
```

#### `test/Workflow/CreateUserSpec.hs` (pure interpreter via newtype)

You can implement a fake repo/log capability in a pure monad (State), then run `createUser` without IO. That is the key architectural benefit: **tests do not require IO or external services**.

---

### 14.8 Why this skeleton blocks OOP-by-translation

1. **Domain invariants are enforced by constructors/smart constructors**, not by "setter-style updates".
2. **Workflows depend on *capabilities*, not on concrete "service objects".**
3. **Side effects are in `App` wiring**, not smeared through business logic.
4. **The code reads as transformations and typed decisions**, not procedural scripts.

---

### Next steps for tightening

* Add explicit "Architecture boundary rule" enforced by module imports (e.g., `Domain` must not import `Effect` or `App`).
* Include QuickCheck/Hedgehog property tests for invariants.
* Document the "effect algebra" you are using and why capabilities were chosen over typeclasses.

---

## Closing note (intentional)

This addendum exists because **Haskell is not "better Java"**.
It is a different way of *thinking* about programs.

> **Haskell code should look inevitable, algebraic, and declarative —
> not procedural code wearing a functional costume.**
