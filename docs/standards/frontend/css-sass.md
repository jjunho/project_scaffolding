# CSS / Sass Language Addendum

**(Cascade Discipline, Token-First Design, Accessibility-Consistent Semantics)**

> This document extends the Universal Project Standard for CSS/Sass projects.
> CSS is treated as a **presentation boundary** with constrained responsibilities.
> All universal rules apply unless explicitly refined here.

---

## Scope

Applies to:

* CSS delivered to browsers (global styles, component styles, CSS Modules, CSS-in-JS outputs).
* Sass/SCSS sources compiled to CSS.
* Utility CSS systems (allowed) as long as they conform to the constraints below.

Non-goals:

* CSS is not a domain layer.
* CSS must not encode business logic or security logic.

---

## 1. Core Principles

### 1.1 CSS is Presentation Only

CSS **MUST** express presentation and layout. It **MUST NOT** encode meaning, logic, or state transitions.

* **MUST NOT** use CSS to represent domain state (e.g., `.is-admin` controlling access, `.paid` implying correctness).
* **MUST NOT** use `display: none` or opacity tricks as security/access control.
* **MUST** derive styling from **explicit semantic state** in markup (attributes, ARIA state, data attributes) that are already correct.

### 1.2 “State Mirrors Semantics” (No Schrödinger UI)

If a user-visible state exists (error, expanded, selected, busy), the semantic source of truth **MUST** be in HTML/DOM attributes; CSS only renders it.

Acceptable state carriers:

* `aria-*` attributes (`aria-expanded`, `aria-invalid`, `aria-checked`, `aria-busy`)
* native states (`:disabled`, `:checked`, `:focus-visible`)
* explicit data attributes (`data-state="open"`, `data-variant="danger"`)

CSS **MUST NOT** invent state via purely visual conventions (e.g., “red border means invalid” with no semantic state).

### 1.3 Cascade Discipline (Minimize Global Blast Radius)

The cascade is power and risk. Uncontrolled global selectors create “action at a distance”.

* **MUST** prefer locally-scoped selectors (component scope, CSS Modules, BEM-like prefixing, or explicit root namespace).
* **MUST NOT** style raw elements globally (`button { ... }`, `h1 { ... }`) except in a documented **base layer**.
* **MUST** treat global styles as an API; breaking changes require review and changelog entry if external-facing.

---

## 2. Architecture: Layering and Ownership

### 2.1 Required Layers

CSS/Sass sources **MUST** be organized into the following conceptual layers (actual folders may vary):

1. **Tokens (Design System primitives)**
   CSS variables for color, spacing, typography, radii, shadows. No selectors.
2. **Base (Resets / defaults)**
   Minimal global element styling; accessibility-safe defaults.
3. **Components (Local styling)**
   Scoped styles for components/features.
4. **Utilities (Optional)**
   Small, explicit helpers with stable meaning (e.g., `.sr-only`).

Rules:

* **MUST** define tokens centrally (prefer `:root` custom properties).
* **MUST** avoid cross-layer imports that create cycles.
* **MUST** declare ownership for shared component libraries.

### 2.2 Tokens are Mandatory

* **MUST** express colors, spacing, typography, and radii via tokens (CSS variables or Sass variables mapped to CSS variables).
* **MUST NOT** scatter raw hex values and arbitrary pixel values through components.
* **MAY** allow literal values only for:

  * borders/hairlines (`1px`)
  * performance-critical one-offs with explicit comment and rationale

---

## 3. Accessibility and Interaction (Merge-Blocking)

### 3.1 Focus is Non-Negotiable

* **MUST** provide visible focus for keyboard users.
* **MUST** use `:focus-visible` for modern focus behavior.
* **MUST NOT** remove focus outlines without an accessible replacement.

Baseline pattern (conceptual):

* Use `:focus-visible` to draw a focus ring.
* Do not rely on color alone; ensure adequate contrast.

### 3.2 Motion and Reduced Motion

* **MUST** respect reduced-motion preferences.
* Any non-trivial animation **MUST** be disabled or simplified under `prefers-reduced-motion: reduce`.

### 3.3 Color is Not Meaning

* **MUST** ensure states are not encoded only via color.
* If CSS changes color for state, the markup must already expose semantic state (e.g., `aria-invalid="true"`).

---

## 4. Forbidden Patterns (Merge-Blocking)

* **Global reach selectors** with high blast radius:

  * `* { ... }` beyond minimal resets
  * deep descendant selectors like `.page .card .title span { ... }` without justification
* **Specificity wars**:

  * repeated `!important` (allowed only in a documented utility layer)
  * stacking selectors to “win” (`.a .b .c .d`)
* **Layout by magic numbers**:

  * “pixel nudges” without tokens or rationale
* **Hidden semantics**:

  * styling that implies state with no semantic source-of-truth

---

## 5. Sass/SCSS-Specific Rules (If Sass is used)

### 5.1 Prefer CSS Variables over Sass Variables for Runtime Theming

* **MUST** use CSS custom properties for values that may vary at runtime (themes, user settings).
* **MAY** use Sass variables for compile-time structure (breakpoints, mixin parameters).

### 5.2 Mixins and Nesting Discipline

* **MUST** keep nesting shallow (recommendation: max 2 levels).
* **MUST NOT** use nesting to encode DOM structure assumptions across the app.
* **MUST** avoid “mixin soup”: mixins must be small, composable, and documented.

### 5.3 No Complex Sass Logic

* **MUST NOT** implement business rules in Sass (loops/conditionals producing state logic).
* Sass is for generating consistent presentation, not encoding domain decisions.

---

## 6. Tooling and CI Enforcement

* **MUST** format CSS/SCSS (Prettier or equivalent).
* **MUST** lint CSS/SCSS (Stylelint recommended) with committed config.
* **MUST** treat lint failures as merge-blocking.
* **SHOULD** detect unused CSS (where toolchain allows) and treat as debt if not blocking.

---

## Final Rule

If the styling:

* changes what the UI “means” without markup semantics,
* breaks keyboard focus visibility,
* relies on global cascade side-effects,
* or uses CSS as a substitute for validation/state,

then it **violates this standard**, even if it “looks correct”.

---

## See Also

* [Appendix — Bad vs Good vs Excellent CSS/Sass](./examples/css-examples.md)
---

## CSS/Sass merge-blockers (review checklist)

A PR fails review if any of the following are true:

1. Focus outlines are removed without a visible replacement.
2. UI state is conveyed only by color with no semantic source-of-truth.
3. Global element styling is added outside the base layer without documentation.
4. Deep selector chains or repeated `!important` are introduced.
5. Non-trivial animations ignore `prefers-reduced-motion`.
6. Tokens are bypassed with repeated raw values without rationale.
