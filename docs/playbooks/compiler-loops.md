# Compiler Loop Playbook (Haskell + Elm)

This playbook captures verified “loop breakers”: recurring compiler/type errors, the typical wrong instinct (often cross-language), the correct language-native model, a canonical fix pattern, and a prevention rule.

Normative use:
- If an AI/human hits the same compile/test failure twice, they MUST perform an assumption reset and either reference an existing entry here or add a new one (verified).
- Entries must remain short, concrete, and runnable/compilable.

Entry template:
1) Symptom (error excerpt)
2) Wrong instinct
3) Correct model
4) Fix pattern (canonical snippet)
5) Prevention
6) Tags

---

## Haskell

### HSK-001 — Text vs String mismatch

1) Symptom  
`Couldn't match expected type ‘Text’ with actual type ‘[Char]’`

2) Wrong instinct  
“Sprinkle conversions everywhere or switch everything back to String.”

3) Correct model  
Choose a canonical representation (usually `Text`) and convert only at boundaries.

4) Fix pattern
```haskell
import Data.Text (Text)
import qualified Data.Text as T

toText :: String -> Text
toText = T.pack

toString :: Text -> String
toString = T.unpack
```

5. Prevention
   Domain types MUST not use `String`. Only IO/parsing layers may convert.

6. Tags
   haskell types text string boundary

### HSK-002 — Partial functions and pattern-match failures

1. Symptom
   Runtime crash: `Non-exhaustive patterns` or `Prelude.head: empty list`

2. Wrong instinct
   “Assume it never happens; add a comment.”

3. Correct model
   Illegal states must be unrepresentable: use `NonEmpty`, `Maybe`, `Either`, ADTs.

4. Fix pattern

```haskell
import Data.List.NonEmpty (NonEmpty(..))
import qualified Data.List.NonEmpty as NE

safeHead :: NonEmpty a -> a
safeHead = NE.head
```

5. Prevention
   Ban `head`, `tail`, `!!`, partial `read`. Add HLint rules or code review blockers.

6. Tags
   haskell safety partial nonempty maybe either

### HSK-003 — “Maybe everywhere” instead of a domain ADT

1. Symptom
   Types balloon into `Maybe (Maybe a)` or `Maybe` chains and fragile branching.

2. Wrong instinct
   “Model unknown states with lots of Maybe; it’s flexible.”

3. Correct model
   Model states explicitly with an ADT; make transitions explicit.

4. Fix pattern

```haskell
data Load a
  = NotAsked
  | Loading
  | Failed Error
  | Loaded a
```

5. Prevention
   If state machine emerges, introduce an ADT. Avoid nested `Maybe` in domain.

6. Tags
   haskell domain modeling adt state-machine

### HSK-004 — Either vs exceptions for recoverable errors

1. Symptom
   Ad-hoc `error`, `undefined`, or exception usage for normal failures.

2. Wrong instinct
   “Throw an exception and catch it somewhere.”

3. Correct model
   Use `Either e a` (or domain error ADT) for recoverable errors; exceptions for truly exceptional.

4. Fix pattern

```haskell
data ParseError = ParseError Text

parseX :: Text -> Either ParseError X
```

5. Prevention
   No `error/undefined` in production modules. Require explicit error types at boundaries.

6. Tags
   haskell errors either exceptions domain

### HSK-005 — IO leakage into pure code

1. Symptom
   `Couldn't match type ‘IO’ with ‘Identity’` / “expected pure, got IO”.

2. Wrong instinct
   “Just make everything IO.”

3. Correct model
   Keep core pure; push effects to the boundary. Use dependency injection via function parameters.

4. Fix pattern

```haskell
-- Pure core
price :: Config -> Order -> Money

-- Effectful boundary
main = do
  cfg <- loadConfig
  ord <- readOrder
  print $ price cfg ord
```

5. Prevention
   Core modules MUST not import `System.*` or perform IO. Effects live in boundary modules.

6. Tags
   haskell io purity boundaries architecture

### HSK-006 — “Monad” confusion: do-notation where Applicative suffices

1. Symptom
   Overuse of `do` blocks where there’s no dependency, leading to unnecessary constraints.

2. Wrong instinct
   “Always use do; it’s clearer.”

3. Correct model
   Use Applicative when independent; it reduces power and increases composability.

4. Fix pattern

```haskell
mkUser :: Text -> Int -> User
mkUser name age = User name age

decodeUser :: Parser User
decodeUser = mkUser <$> parseName <*> parseAge
```

5. Prevention
   Prefer `<$>`, `<*>` unless later steps depend on earlier results.

6. Tags
   haskell applicative monad style composition

### HSK-007 — Newtype for invariants, not type synonyms

1. Symptom
   `type Email = Text` then bugs mixing `Email` and `Name`.

2. Wrong instinct
   “A type alias is enough.”

3. Correct model
   Use `newtype` for distinct meaning and instances.

4. Fix pattern

```haskell
newtype Email = Email { unEmail :: Text }
  deriving stock (Eq, Ord, Show)
```

5. Prevention
   Domain identifiers MUST be `newtype`s. Aliases allowed only for simple structural reuse.

6. Tags
   haskell newtype invariants domain types

### HSK-008 — Record field name clashes / ambiguous selectors

1. Symptom
   `Ambiguous occurrence ‘name’` / conflicting record fields across modules.

2. Wrong instinct
   “Rename fields everywhere randomly.”

3. Correct model
   Use qualified imports, field prefixes, or `DuplicateRecordFields` with discipline.

4. Fix pattern

```haskell
import qualified Domain.User as User

-- Prefer explicit construction and access
User.name user
```

5. Prevention
   Decide a project-wide record field strategy: prefixing or qualified access. Document it.

6. Tags
   haskell records naming modules

### HSK-009 — “Deriving everything” without intent

1. Symptom
   Hard-to-reason instance sets, surprising behavior, orphan instances.

2. Wrong instinct
   “Derive all the things.”

3. Correct model
   Derive only what is necessary; prefer `newtype` wrappers for alternative instances.

4. Fix pattern

```haskell
newtype ByEmail = ByEmail User
  deriving stock (Eq, Show)
  deriving newtype (ToJSON)
```

5. Prevention
   No orphan instances. Alternative ordering/serialization MUST use wrappers.

6. Tags
   haskell instances deriving newtype orphan

### HSK-010 — Fold and traversal: manual recursion or imperative loops

1. Symptom
   Verbose recursion with accumulator bugs.

2. Wrong instinct
   “Write a loop, update variables.”

3. Correct model
   Use `foldMap`, `foldl'`, `traverse`, `mapMaybe`, `partitionEithers`.

4. Fix pattern

```haskell
import Data.Foldable (foldMap)

total :: [Money] -> Money
total = foldMap id
```

5. Prevention
   Prefer standard combinators over bespoke recursion unless performance requires it.

6. Tags
   haskell fold traverse functional idioms

### HSK-011 — Parsing/serialization: “stringly typed” JSON

1. Symptom
   Runtime errors, missing fields, silent defaults.

2. Wrong instinct
   “Just decode into a loose map and pick fields.”

3. Correct model
   Use typed decoders/encoders; keep transport types separate from domain if needed.

4. Fix pattern

```haskell
data UserDTO = UserDTO { email :: Text, age :: Int }
  deriving stock (Generic)
  deriving anyclass (FromJSON, ToJSON)
```

5. Prevention
   Golden fixtures for JSON. Round-trip tests for codecs where applicable.

6. Tags
   haskell json aeson codecs boundary tests

### HSK-012 — Stack/Cabal tool mismatch and “try random flags”

1. Symptom
   Looping on build tool errors: missing packages, wrong resolver, inconsistent versions.

2. Wrong instinct
   “Try installing random system packages or flags until it builds.”

3. Correct model
   Tooling is part of the contract: pin versions, use the project’s chosen tool, follow its docs.

4. Fix pattern

* Stack project: use `stack build`, `stack test`, `stack exec -- ...`
* Ensure `resolver`/`snapshot` pinned and consistent across CI and local.

5. Prevention
   Makefile MUST be the canonical entrypoint for build/test commands.

6. Tags
   haskell tooling stack cabal determinism ci

### HSK-RIO-001 — Missing HasLogFunc instance

1. Symptom
   `No instance for (HasLogFunc env)`

2. Wrong instinct
   Pass logger manually as an argument or remove logging.

3. Correct model
   The RIO environment must satisfy the `HasLogFunc` capability for logging to work.

4. Fix pattern
   Ensure your `Env` type has a `HasLogFunc` instance.
   ```haskell
   data Env = Env { envLogFunc :: !LogFunc, ... }
   instance HasLogFunc Env where
     logFuncL = lens envLogFunc (\x y -> x { envLogFunc = y })
   ```
   Or for scripts: `runSimpleApp action`

5. Prevention
   Define `Env` with `LogFunc` field early and derive the instance.

6. Tags
   haskell rio logging typeclass

### HSK-RIO-002 — Utf8Builder vs String mismatch

1. Symptom
   `Couldn't match expected type Utf8Builder with [Char]`

2. Wrong instinct
   Use `show` or `pack` on everything to make it a String.

3. Correct model
   RIO logging uses `Utf8Builder` for efficiency. Do not use String.

4. Fix pattern
   Enable `OverloadedStrings`.
   Use `<>` for concatenation.
   ```haskell
   {-# LANGUAGE OverloadedStrings #-}
   logInfo $ "Processing item: " <> display item
   ```

5. Prevention
   Always use `Utf8Builder` and `display` / `displayShow` for logging.

6. Tags
   haskell rio logging strings builder

### HSK-RIO-003 — Logging in IO (MonadReader missing)

1. Symptom
   `No instance for (MonadReader env IO)` arising from a use of `logInfo`

2. Wrong instinct
   Change the function signature to `RIO` just to fix the error without understanding boundaries.

3. Correct model
   `logInfo` requires the RIO environment. You are likely in a raw `IO` block.

4. Fix pattern
   Enter the RIO context:
   ```haskell
   runRIO env $ do
     logInfo "Inside RIO"
   ```
   Or use `runSimpleApp`.

5. Prevention
   Keep application logic in `RIO`. Only use `IO` at the very edge or for FFI.

6. Tags
   haskell rio monad-reader boundaries

### HSK-RIO-004 — Temporary environment override

1. Symptom
   Need to temporarily change a value in the environment (e.g., a handle or config) for a sub-computation.

2. Wrong instinct
   Manually construct a new `Env` record and pass it recursively.

3. Correct model
   Use the `Reader` pattern with lenses: `local`.

4. Fix pattern
   ```haskell
   -- Requires Has* instance to provide a Lens, not just a getter
   local (set fieldL newValue) action
   ```

5. Prevention
   Define `Has*` classes with `Lens'` when local modification is required.

6. Tags
   haskell rio lens environment local

---

## Elm

### ELM-001 — Html message type mismatch

1. Symptom
   `This Html is producing MsgA but you need MsgB`

2. Wrong instinct
   “Cast messages or make everything one giant Msg.”

3. Correct model
   Use `Html.map` to lift child messages into parent messages; keep component Msg local.

4. Fix pattern

```elm
viewChild : ChildModel -> Html ChildMsg

view : Model -> Html Msg
view model =
  Html.map ChildMsg (viewChild model.child)
```

5. Prevention
   Component boundaries MUST keep their own Msg/Model. Parent uses mapping.

6. Tags
   elm html msg html.map architecture

### ELM-002 — Cmd/Msg confusion: effects vs messages

1. Symptom
   `This is a Cmd Msg but I need a Msg` or vice versa.

2. Wrong instinct
   “Return commands directly from view or treat Cmd as a value to pattern match.”

3. Correct model
   Effects are returned from `update` as `(Model, Cmd Msg)`; view is pure.

4. Fix pattern

```elm
update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    Save ->
      ( model, saveCmd )
```

5. Prevention
   View MUST not produce Cmd. Effects originate in update/init/subscriptions.

6. Tags
   elm cmd msg update effects tea

### ELM-003 — Maybe misuse for state machines

1. Symptom
   `Maybe` chains and unclear states (`Nothing` could mean many things).

2. Wrong instinct
   “Use Maybe for every optional thing.”

3. Correct model
   State machines should be ADTs.

4. Fix pattern

```elm
type Load a
  = NotAsked
  | Loading
  | Failed String
  | Loaded a
```

5. Prevention
   If `Maybe` starts representing state rather than optional data, replace with an ADT.

6. Tags
   elm adt state-machine maybe modeling

### ELM-004 — JSON decoder shape mismatch

1. Symptom
   `Problem with the given value:` / decoder expects field but gets something else.

2. Wrong instinct
   “Loosen model to match JSON.”

3. Correct model
   Keep domain model; write decoder mapping transport to domain with explicit failures.

4. Fix pattern

```elm
statusDecoder =
  Decode.string
    |> Decode.andThen
        (\s ->
          case s of
            "active" -> Decode.succeed Active
            "disabled" -> Decode.succeed Disabled
            _ -> Decode.fail "unknown status"
        )
```

5. Prevention
   Add fixtures and tests around decoders. Fail explicitly on unknowns unless versioned.

6. Tags
   elm json decoder mapping domain

### ELM-005 — Record update vs rebuild vs “mutable thinking”

1. Symptom
   Overly complex updates, attempts to mutate nested fields.

2. Wrong instinct
   “Update nested state like OOP.”

3. Correct model
   Use record update syntax and helper functions; keep updates local and explicit.

4. Fix pattern

```elm
updateName : String -> Model -> Model
updateName name model =
  { model | name = name }
```

5. Prevention
   Extract small update helpers; avoid deep nesting by structuring model and messages.

6. Tags
   elm records update purity structure

### ELM-006 — Subscriptions misuse (polling in view, effects in wrong place)

1. Symptom
   Trying to subscribe in view or doing time/ports work outside subscriptions/update.

2. Wrong instinct
   “Just call it from view when needed.”

3. Correct model
   Subscriptions are declared from model; update reacts to Msg.

4. Fix pattern

```elm
subscriptions : Model -> Sub Msg
subscriptions model =
  if model.listening then
    Time.every 1000 Tick
  else
    Sub.none
```

5. Prevention
   All ongoing effects MUST be in subscriptions. View remains pure.

6. Tags
   elm subscriptions time tea effects

### ELM-007 — “One giant Msg” vs modular messages

1. Symptom
   Msg grows without structure; update becomes unmaintainable.

2. Wrong instinct
   “Everything in one Msg is simpler.”

3. Correct model
   Use nested Msg types with mapping and module boundaries.

4. Fix pattern

```elm
type Msg
  = Child ChildMsg
  | Save
  | Cancel
```

5. Prevention
   Each feature/component should own its Msg and update; parent composes.

6. Tags
   elm msg modularity composition architecture

### ELM-008 — `Result` vs `Maybe` for failures

1. Symptom
   Silent failure paths or vague `Nothing`.

2. Wrong instinct
   “Use Maybe and ignore why.”

3. Correct model
   Use `Result error value` when failure reasons matter.

4. Fix pattern

```elm
parseInt : String -> Result String Int
```

5. Prevention
   Any user-visible failure MUST preserve an error message.

6. Tags
   elm result maybe errors explicit

### ELM-009 — Effects boundary: Ports for external effects only

1. Symptom
   Trying to “do JS things” inside Elm without ports discipline.

2. Wrong instinct
   “Elm should call into JS whenever it’s easier.”

3. Correct model
   Ports are boundary points. Domain logic stays in Elm; port payloads are typed and minimal.

4. Fix pattern

* Define explicit port messages and encode/decode payloads carefully.
* Keep port interaction in one boundary module.

5. Prevention
   Ports MUST be centralized. Add a typed contract and tests for payload encoding.

6. Tags
   elm ports boundary interop contract

### ELM-010 — UI semantics: CSS-only state without semantic state

1. Symptom
   UI “looks invalid/expanded” but screen readers/DOM semantics don’t reflect it.

2. Wrong instinct
   “Just style it red/open.”

3. Correct model
   State must be explicit in model and reflected in HTML attributes. CSS mirrors semantics.

4. Fix pattern

```elm
input
  [ ariaInvalid (if hasError then "true" else "false")
  ]
  []
```

5. Prevention
   Accessibility rules are merge-blocking: semantic state must exist when visual state exists.

6. Tags
   elm accessibility semantics state html css

### ELM-011 — “Fire and forget” HTTP without state modeling

1. Symptom
   Lost loading/error states, UI doesn’t reflect request lifecycle.

2. Wrong instinct
   “Send request; ignore response or just log it.”

3. Correct model
   Model request lifecycle explicitly; update transitions state.

4. Fix pattern

```elm
type Msg
  = GotUsers (Result Http.Error (List User))

type Load a
  = Loading
  | Failed String
  | Loaded a
```

5. Prevention
   Any HTTP call MUST update a typed load state (Loading/Failed/Loaded).

6. Tags
   elm http result modeling state-machine

### ELM-012 — “I’ll fix it with JS” instead of Elm-native modeling

1. Symptom
   Repeated attempts to bypass Elm constraints via interop.

2. Wrong instinct
   “Elm is too restrictive; use JS.”

3. Correct model
   Elm constraints are guardrails. Prefer Elm-native types and TEA; ports only for unavoidable external integration.

4. Fix pattern

* Introduce an ADT and explicit transitions instead of ad-hoc JS state.

5. Prevention
   Interop is a last resort. Any new port MUST be justified and documented.

6. Tags
   elm architecture ports yolo anti-pattern

---

## Quick Index (Tags)

* Boundaries: HSK-005, HSK-011, ELM-002, ELM-009, ELM-010
* ADTs / state machines: HSK-003, ELM-003, ELM-011
* Errors: HSK-004, ELM-008, ELM-011
* JSON: HSK-011, ELM-004
* Tooling/CI: HSK-012
* Anti OOP projection: HSK-005, ELM-012

---

## Contribution rules

* Keep entries short.
* Include an exact symptom excerpt when possible.
* Ensure fix pattern compiles or is a canonical idiom.
* Always add a prevention rule.
* Prefer language-native reasoning; ban cross-language projection.
