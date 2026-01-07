# Dyalog APL Constitution

**(Array-native, shape-driven, explicit contracts, maintainable concision)**

This document defines the minimum acceptable standard for professional Dyalog APL code. It exists to prevent “clever APL” (write-only, session-dependent, implicit) from becoming a maintenance liability.

If a function’s correctness depends on the author remembering what a vector “usually contains,” it violates this constitution.

## 1. Fundamental rule

APL code MUST be designed in terms of **arrays, shapes, ranks, and transformations**.
All meaning must be recoverable from:

* the function’s name and header comment,
* the **shape contract** (rank, axes, units),
* and the sequence of transformations.

If meaning lives primarily in “column 3 is X” without an explicit contract, the code is not acceptable.

---

## 2. Shape contracts are mandatory

### 2.1 Every non-trivial function MUST state a shape contract

At minimum, a function header comment MUST include:

* expected rank(s) and key axis meaning
* constraints (non-empty, sorted, unique, domain)
* output shape and interpretation

Example (acceptable):

```apl
⍝ input: users is N×4 (id name email status)
⍝ output: activeUsers is M×4 subset, preserving column semantics
```

### 2.2 Matrix Schemas and Validation

When using matrices as data tables, you MUST document the schema and provide a validation function.

**Proposta de notação de Schema:**

```apl
⍝ SCHEMA: users[N×4]
⍝   [;1] id:int (unique, positive)
⍝   [;2] name:char
⍝   [;3] email:char (validated format)
⍝   [;4] status:char ∊ 'active' 'inactive' 'pending'
```

**Exemplo de Validação de Schema:**

```apl
ValidateUsers←{
    ⍝ ⍵: alleged users matrix
    ⍝ ←: 1=valid | 0=invalid
    (2=≢⍴⍵)∧(4=¯1↑⍴⍵)∧(∧/0<⍵[;1])∧(∧/⍵[;4]∊⊂'active' 'inactive' 'pending')
}
```

### 2.3 Boundary Invariants MUST be enforced

APL does not give you “types” in the Haskell sense. Your “types” are:

* shape (⍴)
* rank (⍴⍴)
* element type (numeric/char/nested)
* domain constraints (ranges, membership, uniqueness, sortedness)

You MUST validate or normalize once, early, then keep core transforms simple.

### 2.4 Handling Edge Cases and Rank Invariants

Contracts MUST specify behavior for empty arrays and rank mismatches.

```apl
⍝ CONTRACT VIOLATION: what if ⍵ is empty?
Sum←{+/⍵}  ⍝ breaks on ⍬

⍝ EXPLICIT CONTRACT:
Sum←{
    ⍝ ⍵: numeric vector (may be empty)
    ⍝ ←: scalar sum (0 if empty)
    0=≢⍵: 0
    +/⍵
}
```

---

## 3. Pure core, explicit boundaries

### 3.1 Boundary code is special and must be isolated

Boundary = file I/O, database calls, HTTP, UI, ⎕N*, ⎕SQL, JSON parse/format, external process invocation, COM/.NET, etc.

Rules:

* Boundary modules MAY be effectful.
* Core transformation modules SHOULD be pure: arrays in, arrays out.
* Boundary code MUST convert external representations into **internal canonical arrays** (with documented shape contracts).

---

## 4. Default to dfns (and be deliberate about dfn vs tradfn)

### 4.1 Prefer dfns for compositional, local-scope code

* dfns give lexical scoping, local variables, clear composition, and are idiomatic in modern Dyalog.

### 4.2 Use tradfns when they improve clarity for complex procedural boundaries

Tradfns are fine for orchestration-heavy tasks (file I/O, UI event loops), but the “array core” should remain dfn-centric.

---

## 5. Concision is a tool; readability is a constraint

APL’s power comes from dense expressions. Professional APL is dense **and still readable**.

Rules:

* Use trains/tacit style when the intent is obvious.
* Switch to explicit dfns when tacit obscures shape changes or domain meaning.
* Avoid “one-liners” that hide multiple conceptual steps.

A good reviewer rule:

If a competent APL engineer cannot explain the expression in 20–30 seconds, it is too clever.

---

## 6. Idiomatic transformation patterns (Dyalog)

These are “default moves” in idiomatic Dyalog APL.

### 6.1 Filtering: replicate/compress, not loops

Prefer masking followed by compression. Avoid explicit iteration for selection.

```apl
⍝ BAD: procedural loop
FilterActive←{
    result←0 4⍴⍬
    :For row :In ↓⍵
        :If 4⊃row ≡ 'active'
            result⍪←row
        :EndIf
    :EndFor
    result
}

⍝ IDIOMATIC: array mask + compress
FilterActive←{
    ⍝ ⍵: N×4 matrix (id name email status)
    ⍝ ←: M×4 matrix, rows where status='active'
    mask←'active'≡¨⍵[;4]
    mask⌿⍵
}
```

### 6.2 Grouping: key (`⌸`) progression

Use `⌸` for grouping by keys. Progression of idioms:

```apl
⍝ BASIC: count occurrences
data←'apple' 'banana' 'apple' 'cherry' 'banana' 'apple'
{≢⍵}⌸data
⍝ → 'apple' (3) | 'banana' (2) | 'cherry' (1)

⍝ INTERMEDIATE: sum by key
keys←'A' 'B' 'A' 'C' 'B' 'A'
vals←10 20 30 40 50 60
keys{⍺,⊂+/⍵}⌸vals
⍝ → ('A' 100) ('B' 70) ('C' 40)

⍝ ADVANCED: group matrix rows by column
sales←4 3⍴'A' 100 5 'B' 200 3 'A' 150 2 'B' 100 4
sales[;1]{⍺,⊂+⌿⍵[;2 3]}⌸sales
⍝ → group by product (col 1), sum quantity+price (cols 2-3)
```

### 6.3 Performance vs Clarity: Trade-offs

APL can be extremely conciso, but maintain a rule: "optimize after measuring, not before".

```apl
⍝ CLEAR but creates intermediate arrays:
Result←(+/data)÷≢data

⍝ EFFICIENT but less obvious:
Result←(+/data)÷⍴data  ⍝ ⍴ on vector = single number, faster
```

For large matrices:

* **CLEAR**: `mask/⍨data` (creates boolean intermediate)
* **FAST**: `(data⊣mask)/data` (avoids some copying)

### 6.4 Aggregation: reduce (`/`) and scan (`\`) with clear intent

* `+/` sums
* `∨/` any
* `∧/` all
* scans for running totals, cumulative flags

Prefer these to explicit counters.

### 6.4 Sorting/grade: `⍋` / `⍒` and indexing

Idiomatic APL uses grade then index, not ad-hoc sorting loops.

### 6.5 Membership and set logic: `∊`, `⍷`, `∩`, `∪`, `~`

Choose set primitives over manual “contains” loops; document complexity expectations.

### 6.6 Shape and rank are first-class: `⍴`, `≢`, `,`, `⍉`, `⌽`, `⊖`

Reshape and transpose intentionally and visibly. Hidden reshapes are maintenance hazards.

---

## 7. Nested arrays vs simple arrays: choose intentionally

### 7.1 Simple arrays are preferred for performance and clarity

Use simple numeric/char arrays when the data is rectangular.

### 7.2 Nested arrays are for irregular data

When irregularity is real, nested arrays are idiomatic. But you MUST document the nesting level and structure.

**Heuristics:**

* **Ragged data** (variable length sublists) → Embrace nested arrays.
* **Rectangular data** (regular shape) → Use simple arrays.

```apl
⍝ AVOID: nested when simple works
data←(1 2 3)(4 5 6)(7 8 9)  ⍝ WRONG: should be matrix
data←3 3⍴⍳9                ⍝ RIGHT: simple matrix

⍝ GOOD: when truly irregular
messages←('hello')('' 'world' 'foo')('x')  ⍝ variable-length sublists
lengths←≢¨messages                          ⍝ → 1 3 1
```

---

## 8. Namespaces and modularity (Dyalog)

### 8.1 Avoid “utils” dumping grounds

Helpers belong next to the concept they serve.

### 8.2 Organize by domain concept + shape contract

Example structure:

* `User/Normalize`
* `User/Validate`
* `User/Filter`
* `User/Aggregate`

Each module should “own” its shape conventions.

---

## 9. System variables: make them explicit and stable

Dyalog has globals that can silently change semantics.

Rules:

* The project MUST define and enforce a standard for `⎕IO`, `⎕ML`, `⎕PP`, and any other relevant system settings.
* Modules MUST NOT rely on “whatever the session currently has.”
* If a module depends on a specific setting, set it locally and restore (or enforce at startup).

**Standard Enforcement Example:**

```apl
⍝ project_init.dyalog
⎕IO←0  ⍝ MANDATORY: 0-indexed (consistent with most modern systems)
⎕ML←1  ⍝ Migration level 1 (modern semantics)
⎕PP←10 ⍝ Print precision

⍝ Enforcement via assertion trap:
Assert←{⍺←'assertion failed' ⋄ ⍵:shy←⍬ ⋄ ⎕SIGNAL⊂('EN' 11)('Message' ⍺)}

CheckEnv←{
    'IO must be 0'Assert ⎕IO=0
    'ML must be 1'Assert ⎕ML=1
    ⍬
}

⍝ Call at module load:
CheckEnv⍬
```

---

## 10. Error handling is values + contracts, not ad-hoc traps

Rules:

* Use explicit validation results when domain failure is expected.
* Do not treat LENGTH ERROR / DOMAIN ERROR as business logic branches.
* Use traps for boundary unpredictability (I/O), not for routine domain decisions.

**Recommended Patterns:**

```apl
⍝ PATTERN 1: Maybe monad (0=error | 1=ok, value)
ParseInt←{
    ⍝ ⍵: char vector
    ⍝ ←: (ok value) where ok∊0 1
    ~∧/⍵∊⎕D: 0 ¯1  ⍝ error: invalid chars
    1(⍎⍵)          ⍝ ok: return parsed value
}

⍝ PATTERN 2: Either monad (left=error | right=value)
Divide←{
    ⍝ ⍵: x y (numbers)
    ⍝ ←: ('error' msg) | ('ok' result)
    (x y)←⍵
    y=0: ('error' 'division by zero')
    ('ok' (x÷y))
}

⍝ PATTERN 3: Enclosing for multiple errors
ValidateUser←{
    ⍝ ⍵: user matrix row
    ⍝ ←: ⍬ se ok | vector of error messages
    errors←⍬
    ~(⍵[1])∊⎕D: errors,←⊂'invalid id'
    0=≢⍵[2]: errors,←⊂'name required'
    errors
}
```

---

# Transformation Recipes (Receituário)

### 1. Transpose grouped data (pivot)

Input: (key val) pairs → Output: unique keys, aggregated values

```apl
sales←('A' 10)('B' 20)('A' 15)('C' 5)('B' 25)
keys←⊃¨sales
vals←⊃∘⌽¨sales
result←(∪keys){⍵,+/vals[⍸keys≡¨⊂⍵]}¨∪keys
```

### 2. Running window (sliding)

Input: vector → Output: overlapping subarrays

```apl
Window←{
    ⍝ ⍺: window size
    ⍝ ⍵: data vector
    ⍝ ←: matrix where each row is a window
    n←≢⍵
    (n-⍺+1)≥0: ⍵[⍺,⍺+⍳n-⍺+1]
    ⍬
}
3 Window ⍳10  ⍝ → windows of size 3
```

### 3. Join/merge (SQL-like)

```apl
⍝ users: N×2 (id name)
⍝ orders: M×3 (order_id user_id amount)
users←3 2⍴1 'Alice' 2 'Bob' 3 'Charlie'
orders←4 3⍴101 1 50 102 2 30 103 1 20 104 3 100

JoinOrders←{
    ⍝ ⍺: users | ⍵: orders
    uids←⍺[;1]
    oids←⍵[;2]
    mask←oids∊uids
    matched←mask/⍵
    idx←uids⍳matched[;2]
    ⍺[idx;],matched[;1 3]  ⍝ combine: name, order_id, amount
}
users JoinOrders orders
```

---

# Advanced Modeling Patterns

### State machines in APL

```apl
⍝ State machine for simple expression parsing
ParseExpr←{
    ⍝ ⍵: char vector like '3+5*2'
    ⍝ ←: (valid tokens) | error message
    state←0
    tokens←⍬
    :For char :In ⍵
        :Select state
        :Case 0  ⍝ start
            :If char∊⎕D ⋄ state←1 ⋄ tokens,←⊂char
            :Else ⋄ :Return 'error: expected digit' ⋄ :EndIf
        :Case 1  ⍝ number
            :If char∊⎕D ⋄ tokens[≢tokens],←char
            :ElseIf char∊'+-*/' ⋄ state←2 ⋄ tokens,←⊂char
            :Else ⋄ :Return 'error: unexpected char' ⋄ :EndIf
        :Case 2  ⍝ operator
            :If char∊⎕D ⋄ state←1 ⋄ tokens,←⊂char
            :Else ⋄ :Return 'error: expected digit after operator' ⋄ :EndIf
        :EndSelect
    :EndFor
    state∊0 2: 'error: incomplete expression' ⋄ tokens
}
```

### Memoization (Cache)

```apl
:Namespace Fib
    cache←⍬
    Compute←{
        ⍝ ⍵: n (integer)
        ⍝ ←: fibonacci(n)
        ⍵<≢cache: cache[⍵]
        result←⍵<2: ⍵ ⋄ (∇ ⍵-1)+∇ ⍵-2
        cache↑⍨←⍵+1
        cache[⍵]←result
        result
    }
:EndNamespace
```

---

# Skill Progression (Progressão de Habilidades)

* **Level 1:** Shape contracts, filter/compress, basic reduce, dfns.
* **Level 2:** Key (⌸), nested arrays, tacit composition, trains.
* **Level 3:** Custom operators, performance tuning, system variable enforcement.

---

# APL Idioms Glossary (Glossário de Idiomas)

| Idiom | Code | Usage |
| :--- | :--- | :--- |
| Unique | `∪⍵` | remove duplicates |
| Count occurrences | `{≢⍵}⌸⍵` | histogram / counts |
| Index of max | `⍵⍳⌈/⍵` | position of largest |
| Running sum | `+\⍵` | cumulative total |
| Boolean to indices | `⍸mask` | find true positions |

---

# A reviewer-grade checklist (APL)

These are merge-blocking unless explicitly justified.

1. **Shape contracts** exist for non-trivial functions and are accurate.
2. **Boundary code** is isolated; core transforms are arrays-in/arrays-out.
3. **No session-dependency**: System variables (`⎕IO`, `⎕ML`) are standardized and enforced.
4. **No positional magic**: Matrix schemas are documented and validated.
5. **No procedural loops**: Standard array operators apply (unless performance profiling proves necessity).
6. **Edge Case Handling**: Empty arrays (`⬬`, `⍬`) and rank-1 vs rank-2 cases are handled.
7. **Key Documentation**: All `⌸` usages document the structure of the resulting nested array.
8. **Nesting Awareness**: Nested arrays are used only when irregularity is real; depth is documented (`≡⍵`).
9. **Tacit usage** is readable; otherwise, use explicit dfns.
10. **Errors**: Validation is explicit (Maybe/Either patterns); runtime errors/traps are not control flow.

---

# Template de Módulo

```apl
:Namespace ModuleName
⍝ PURPOSE: [one-line description]
⍝ DEPENDENCIES: [list other namespaces]
⍝ SCHEMA CONTRACTS: [list matrix/array formats this module expects]
⍝ SYSTEM REQUIREMENTS: ⎕IO←0, ⎕ML←1

    ⍝ === PUBLIC API ===
    
    PublicFunction←{
        ⍝ [detailed contract]
        ⍝ implementation
    }
    
    ⍝ === PRIVATE HELPERS ===
    
    _helper←{
        ⍝ [contract]
    }
    
    ⍝ === TESTS (if inline) ===
    
    Test←{
        ⍝ assertions
    }

:EndNamespace
```

---

## See also

* [Universal Project Standard](STANDARD.md) — Language-agnostic baseline
* [Elm Language Addendum](elm.md) — Reference for functional purity
* [Haskell Language Addendum](haskell.md) — Reference for type-driven design (emulated via shapes)
