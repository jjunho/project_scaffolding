# HTML Language Addendum

**(Semantic Structure, Accessibility-First, Explicit Boundaries)**

> **This document extends the Universal Project Standard for HTML projects.**
> It treats HTML as a strict **boundary** and **correctness constraint**, not a presentation layer.
> All universal rules apply unless explicitly refined here.

---

## Scope

Applies to:

* All HTML documents delivered to browsers (SPA entry points, server-rendered templates, static sites).
* JSX/TSX, Elm `Html`, Vue templates, or other languages that compile to HTML.

---

## 1. Core Principles

### 1.1 Semantic Structure is Mandatory

HTML **MUST** describe the *structure and meaning* of content, not its presentation.

* **MUST** use landmark elements (`<main>`, `<nav>`, `<header>`, `<footer>`, `<aside>`) to define page structure.
  * **MUST** have exactly one `<main>` per page.
  * **MUST NOT** nest `<main>` inside `<article>`, `<section>`, or `<aside>`.
* **MUST** use correct heading hierarchy (`<h1>` through `<h6>`) without skipping levels.
* **MUST** use `<button>` for actions and `<a>` for navigation.
  * **MUST NOT** attach click handlers to `<div>` or `<span>` without explicit ARIA roles and keyboard handling.

### 1.2 Accessibility (a11y) is a Baseline, not a Feature

* **MUST** comply with **WCAG 2.1 Level AA**.
* **First Rule of ARIA**: Don't use ARIA if a native HTML element provides the semantics.
  * **MUST NOT** add ARIA roles that duplicate native semantics (e.g., `role="button"` on `<button>`).
* **MUST** ensure all interactive elements are keyboard accessible (focusable and actionable).

---

## 2. HTML is a Boundary, Not a Container

Every other document in this project treats boundaries as *correctness choke points*. HTML is the boundary between **Domain/UI State** and **The User / Assistive Technology / Machines**.

### Rules

* **MUST** ensure **Logical Reading Order**:
  * DOM order **MUST** match visual reading order, keyboard navigation order, and screen-reader reading order.
  * **MUST NOT** rely on CSS reordering (`flex-order`, `grid-area`) to change logical meaning.
* **MUST NOT** encode domain invariants implicitly via CSS or layout.
* **MUST** expose state changes via semantics (`aria-live`, roles) when relevant.
* **MUST** treat the DOM as an **output artifact** of state, not a storage mechanism for state.

---

## 3. Illegal States Must Be Unrepresentable (HTML Edition)

Just as we ban illegal states in Haskell/Elm types, we ban them in markup. The following states are **violations**:

* **Unreachable Action**: A clickable element that cannot be reached or activated via keyboard.
* **Anonymous Control**: A form input without an associated label.
* **Schrodinger's State**: Visual state (e.g., "error red") without semantic state (e.g., `aria-invalid="true"`).
* **Orphaned Content**: Meaningful content outside of a landmark region.
* **Ambiguous Button**: A button containing only an icon without an `aria-label` or screen-reader-only text.

**Enforcement**: These are **merge-blocking defects**, not style nitpicks.

---

## 4. Accessibility Deep Rules

* **MUST** provide visible focus styles (CSS `outline` or equivalent). **MUST NOT** remove default outline without replacing it.
* **MUST** ensure color is never the sole carrier of meaning.
* **MUST** ensure sufficient contrast (4.5:1 for normal text).
* **MUST** avoid `tabindex > 0`. Positive tabindex destroys natural flow.
* **Visibility Sync**:
  * **MUST NOT** hide focusable or meaningful content using `aria-hidden="true"`.
  * **MUST** keep semantic visibility in sync with visual visibility. If content is visually hidden but meaningful, use screen-reader-only patterns.

---

## 5. Forms as State Machines

* **MUST** associate labels with inputs explicitly via `for`/`id` nesting.
* **MUST** associate error messages with inputs via `aria-describedby`.
* **MUST** reflect validation state semantically via `aria-invalid="true"`.
* **MUST NOT** rely solely on placeholder text as a label.
* **MUST** use appropriate `type` attributes (email, tel, number) to trigger correct virtual keyboards.
* **MUST** use `<fieldset>` and `<legend>` for groups of related inputs.

---

## 6. HTML / CSS / JS Contract

* **HTML**: Defines Structure, Semantics, and State.
* **CSS**: Defines Presentation only.
* **JS**: Defines Behavior and State mutations.

**Normative Constraints**:

* **JS MUST NOT** fix missing semantics (e.g., adding `role="button"` to a div at runtime). Fix the markup.
* **CSS MUST NOT** encode logic (e.g., using `display: none` to manage security or access control).
* **State MUST** be reflected in HTML attributes when user-relevant (e.g., `aria-expanded`).

---

## 7. Anti-Patterns (Forbidden)

* **Div Soup**: Excessive nesting of generic containers (`<div>`).
* **Inline Styles**: Usage of `style="..."` is **PROHIBITED** (except for dynamic values calculated at runtime).
* **Inline Scripts**: `<script>` tags with body content are **PROHIBITED** (security risk/CSP violation).
* **Presentation in Markup**: Using tags like `<b>`, `<i>`, `<br>` for layout purposes.

---

## 8. Enforcement & CI

* **MUST** validate HTML/a11y in CI (e.g., `html-validate`, `axe-core`).
* **MUST** treat a11y violations as **merge-blocking** build failures.
* Local development (`make check`) and CI **MUST** enforce the same HTML/a11y rules.

---

## 9. Exceptions & Legacy Handling

* **Data Viz**: Complex SVGs **MAY** bypass strict semantic rules if provided with a fallback text description.
* **Legacy**: Legacy pages **MUST** be brought up to standard when touched.

Any permanent exception **MUST** be documented in an ADR.

---

## 10. HTML PR Reviewer Checklist (Merge-Blocking)

* [ ] All actions reachable and actionable by keyboard.
* [ ] All inputs have explicit, persistent labels.
* [ ] Exactly one `<main>` landmark exists and is not nested incorrectly.
* [ ] DOM order matches visual and navigation reading order.
* [ ] No visual-only state (color/icon without semantic attribute).
* [ ] No ARIA roles duplicating native element semantics.
* [ ] No JS "fixing" missing markup semantics.

---

## Final Rule

If the markup relies on CSS to convey meaning, is not navigable by keyboard, or allows a state where the visual reality contradicts the semantic reality, then it **violates this standard**.

---

## See Also

* [Appendix A — Bad vs Good vs Excellent HTML](./examples/html-examples.md)
* [Appendix C — Bad vs Good vs Excellent JSX/TSX](./examples/jsx-tsx-examples.md)