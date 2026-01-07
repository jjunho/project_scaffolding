# Appendix A — Bad vs Good vs Excellent HTML

> This document provides reviewer-grade examples for the [HTML Constitution](../html.md).

### A.1 Actions vs Navigation

Bad (div-as-button, not keyboard accessible, no semantics)

```html
<div class="btn" onclick="save()">Save</div>
```

Good (native semantics, keyboard works)

```html
<button type="button" class="btn" onclick="save()">Save</button>
```

Excellent (explicit state + disabled semantics, resilient to styling)

```html
<button
  type="button"
  class="btn"
  aria-busy="true"
  disabled
>
  Saving…
</button>
```

Reviewer notes:

* “Good” is usually sufficient.
* “Excellent” matters when async state exists (prevents double-submit and conveys progress).

---

### A.2 Icon-only controls

Bad (ambiguous, inaccessible name)

```html
<button type="button"><svg aria-hidden="true">...</svg></button>
```

Good (aria-label provides accessible name)

```html
<button type="button" aria-label="Close">
  <svg aria-hidden="true">...</svg>
</button>
```

Excellent (visible + SR-only name, avoids reliance on ARIA alone)

```html
<button type="button">
  <svg aria-hidden="true">...</svg>
  <span class="sr-only">Close</span>
</button>
```

Reviewer notes:

* “Good” is acceptable for many systems; “Excellent” is preferable if you already have an `sr-only` utility.

---

### A.3 Headings and document outline

Bad (skips levels; layout-driven headings)

```html
<h1>Dashboard</h1>
<h3>Recent Activity</h3>
```

Good (no skipping)

```html
<h1>Dashboard</h1>
<h2>Recent Activity</h2>
```

Excellent (sections with meaningful headings; scalable structure)

```html
<main>
  <h1>Dashboard</h1>

  <section aria-labelledby="recent-activity-title">
    <h2 id="recent-activity-title">Recent Activity</h2>
    ...
  </section>
</main>
```

Reviewer notes:

* “Excellent” helps when pages grow; it reduces ad-hoc ARIA later.

---

### A.4 Landmark structure

Bad (no landmarks; “div soup”)

```html
<div class="header">...</div>
<div class="content">...</div>
<div class="footer">...</div>
```

Good (landmarks)

```html
<header>...</header>
<main>...</main>
<footer>...</footer>
```

Excellent (distinct navs, clear structure)

```html
<header>
  <nav aria-label="Primary">...</nav>
</header>

<main id="content">...</main>

<footer>
  <nav aria-label="Footer">...</nav>
</footer>
```

Reviewer notes:

* Require exactly one `<main>` per page.
* Multiple `<nav>` is fine only if purpose is distinct and labeled.

---

### A.5 Toggle controls (expanded/collapsed)

Bad (visual toggle only; no semantic state)

```html
<button type="button" onclick="toggleMenu()">Menu</button>
<div id="menu" class="hidden">...</div>
```

Good (aria-expanded + aria-controls)

```html
<button
  type="button"
  aria-expanded="false"
  aria-controls="menu"
  onclick="toggleMenu()"
>
  Menu
</button>

<div id="menu" hidden>...</div>
```

Excellent (state reflected consistently; no contradictory reality)

```html
<button
  type="button"
  aria-expanded="true"
  aria-controls="menu"
>
  Menu
</button>

<div id="menu">...</div>
```

Reviewer notes:

* The “Excellent” pattern assumes your rendering updates both `aria-expanded` and visibility together.
* Prefer `hidden` for “not visible and not interactive”; avoid “CSS only” hiding for semantic state.

---

### A.6 Forms: labeling

Bad (placeholder as label)

```html
<input type="email" placeholder="Email">
```

Good (explicit label association)

```html
<label for="email">Email</label>
<input id="email" type="email" autocomplete="email">
```

Excellent (help text + stable association)

```html
<label for="email">Email</label>
<input id="email" type="email" autocomplete="email" aria-describedby="email-help">
<p id="email-help">We’ll only use this for account recovery.</p>
```

Reviewer notes:

* Placeholders can exist, but never as the only label.

---

### A.7 Forms: errors as semantic state

Bad (red border only; no semantic signal)

```html
<label for="email">Email</label>
<input id="email" class="error" type="email">
<p class="error-text">Invalid email</p>
```

Good (`aria-invalid` + `aria-describedby`)

```html
<label for="email">Email</label>
<input
  id="email"
  type="email"
  aria-invalid="true"
  aria-describedby="email-error"
>
<p id="email-error">Invalid email</p>
```

Excellent (error region is announced; resilient UX)

```html
<label for="email">Email</label>
<input
  id="email"
  type="email"
  aria-invalid="true"
  aria-describedby="email-error"
>

<p id="email-error" role="alert">
  Invalid email
</p>
```

Reviewer notes:

* Use `role="alert"` selectively (for user-relevant, immediate errors). Do not turn the whole page into alerts.

---

### A.8 Radio groups and checkboxes

Bad (no grouping semantics)

```html
<p>Plan</p>
<input type="radio" name="plan" id="p1"><label for="p1">Basic</label>
<input type="radio" name="plan" id="p2"><label for="p2">Pro</label>
```

Good (`fieldset` + `legend`)

```html
<fieldset>
  <legend>Plan</legend>

  <div>
    <input type="radio" name="plan" id="p1">
    <label for="p1">Basic</label>
  </div>

  <div>
    <input type="radio" name="plan" id="p2">
    <label for="p2">Pro</label>
  </div>
</fieldset>
```

Excellent (adds help text association)

```html
<fieldset aria-describedby="plan-help">
  <legend>Plan</legend>
  <p id="plan-help">You can change plans at any time.</p>
  ...
</fieldset>
```

---

### A.9 Links: correct usage

Bad (link used as button; confusing semantics)

```html
<a href="#" onclick="logout()">Log out</a>
```

Good (button for action)

```html
<button type="button" onclick="logout()">Log out</button>
```

Excellent (button that communicates busy state if needed)

```html
<button type="button" aria-busy="true" disabled>
  Logging out…
</button>
```

---

### A.10 Tables: data vs layout

Bad (table for layout)

```html
<table>
  <tr><td>Label</td><td>Value</td></tr>
</table>
```

Good (table for real data with headers)

```html
<table>
  <thead>
    <tr><th scope="col">Metric</th><th scope="col">Value</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Users</th><td>1,245</td></tr>
  </tbody>
</table>
```

Excellent (caption clarifies meaning)

```html
<table>
  <caption>Usage metrics for January 2026</caption>
  ...
</table>
```

Reviewer notes:

* If it’s not a data table, don’t use `<table>`.

---

### A.11 Images: meaningful vs decorative

Bad (missing alt; screen readers read filename or nothing)

```html
<img src="/hero.png">
```

Good (meaningful image)

```html
<img src="/hero.png" alt="Students collaborating in a classroom">
```

Excellent (decorative image explicitly ignored)

```html
<img src="/sparkle.svg" alt="" aria-hidden="true">
```

Reviewer notes:

* Decorative images should not pollute the accessibility tree.

---

### A.12 DOM order and CSS reordering

Bad (CSS order changes meaning; keyboard/AT order breaks)

```html
<div class="row">
  <button class="secondary">Cancel</button>
  <button class="primary">Confirm</button>
</div>
```

```css
.row { display: flex; }
.primary { order: 0; }
.secondary { order: 1; }
```

Good (DOM order matches intended reading/action order)

```html
<div class="row">
  <button class="primary">Confirm</button>
  <button class="secondary">Cancel</button>
</div>
```

Excellent (logical grouping + clear intent, still DOM-first)

```html
<div class="row" role="group" aria-label="Confirmation">
  <button class="primary">Confirm</button>
  <button class="secondary">Cancel</button>
</div>
```

Reviewer notes:

* Do not rely on CSS `order` to change meaning.
