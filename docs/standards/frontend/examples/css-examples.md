# Appendix — Bad vs Good vs Excellent CSS/Sass

> This document provides reviewer-grade examples for the [CSS/Sass Language Addendum](../css-sass.md).

### D.1 Focus outlines

Bad (removes focus; accessibility regression)

```css
button:focus {
  outline: none;
}
```

Good (visible focus with modern behavior)

```css
button:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}
```

Excellent (tokenized, reusable focus ring pattern)

```css
:root {
  --focus-ring: #1a73e8;
  --focus-ring-offset: 2px;
  --focus-ring-width: 2px;
}

:where(a, button, input, select, textarea):focus-visible {
  outline: var(--focus-ring-width) solid var(--focus-ring);
  outline-offset: var(--focus-ring-offset);
}
```

Reviewer notes:

* Focus visibility is merge-blocking.

---

### D.2 State derived from semantics (no Schrödinger UI)

Bad (CSS invents “invalid”)

```css
.input.error {
  border-color: red;
}
```

Good (semantic attribute drives presentation)

```css
input[aria-invalid="true"] {
  border-color: var(--color-danger);
}
```

Excellent (semantic state drives multiple cues; not color-only)

```css
input[aria-invalid="true"] {
  border-color: var(--color-danger);
}

input[aria-invalid="true"]:focus-visible {
  outline-color: var(--color-danger);
}
```

---

### D.3 Avoid global element styling outside base layer

Bad (global blast radius)

```css
button {
  border-radius: 999px;
  font-weight: 600;
}
```

Good (component class)

```css
.btn {
  border-radius: var(--radius-pill);
  font-weight: 600;
}
```

Excellent (scoped component + variant tokens)

```css
.btn {
  border-radius: var(--radius-pill);
  font-weight: 600;
}

.btn[data-variant="primary"] {
  background: var(--color-primary);
}

.btn[data-variant="danger"] {
  background: var(--color-danger);
}
```

---

### D.4 Specificity control

Bad (specificity war)

```css
.page .card .header .title span {
  font-size: 18px;
}
```

Good (single class, explicit intent)

```css
.cardTitle {
  font-size: var(--font-size-lg);
}
```

Excellent (use :where to lower specificity when needed)

```css
:where(.cardTitle) {
  font-size: var(--font-size-lg);
}
```

---

### D.5 `!important` discipline

Bad (spreads and becomes unmaintainable)

```css
.btn {
  color: white !important;
}
```

Good (fix the cascade, not the symptom)

```css
.btn {
  color: var(--color-on-primary);
}
```

Excellent (reserved utility layer only)

```css
/* utilities.css */
.u-hidden {
  display: none !important;
}
```

Reviewer notes:

* `!important` is allowed only in documented utility layer.

---

### D.6 Reduced motion

Bad (forces animation)

```css
.modal {
  transition: transform 300ms ease;
}
```

Good (respects reduced motion)

```css
.modal {
  transition: transform 300ms ease;
}

 @media (prefers-reduced-motion: reduce) {
  .modal {
    transition: none;
  }
}
```

Excellent (system-wide pattern)

```css
 @media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
    scroll-behavior: auto !important;
  }
}
```

---

### D.7 Sass nesting discipline

Bad (deep nesting couples to DOM structure)

```scss
.page {
  .card {
    .header {
      .title {
        span {
          font-weight: 700;
        }
      }
    }
  }
}
```

Good (flat selectors)

```scss
.cardTitle {
  font-weight: 700;
}
```

Excellent (tokens + shallow nesting for variants)

```scss
.btn {
  border-radius: var(--radius-md);

  &[data-variant="primary"] {
    background: var(--color-primary);
  }
}
```
