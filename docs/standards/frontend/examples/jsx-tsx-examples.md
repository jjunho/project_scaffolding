# Appendix C — Bad vs Good vs Excellent JSX/TSX

> This document provides framework-aware examples for JSX/TSX ecosystems, enforcing the [HTML Constitution](./html.md) and [Typed Frontend Constitution](./TYPED_FRONTEND_CONSTITUTION.md).

---

### C.1 “Clickable div” and fake buttons

Bad (div-as-button; broken keyboard semantics)

```tsx
export function SaveCard() {
  return (
    <div className="btn" onClick={() => save()}>
      Save
    </div>
  )
}
```

Good (native button)

```tsx
export function SaveCard() {
  return (
    <button type="button" className="btn" onClick={() => save()}>
      Save
    </button>
  )
}
```

Excellent (explicit disabled/busy state + prevents double click)

```tsx
type Props = { isSaving: boolean; onSave: () => void }

export function SaveButton({ isSaving, onSave }: Props) {
  return (
    <button
      type="button"
      className="btn"
      aria-busy={isSaving}
      disabled={isSaving}
      onClick={onSave}
    >
      {isSaving ? "Saving…" : "Save"}
    </button>
  )
}
```

Reviewer notes:

* If it is an action, it is a `<button>`.
* “Excellent” is required when async state exists.

---

### C.2 Links used as buttons (common SPA antipattern)

Bad (anchor for action; breaks semantics, may break routing)

```tsx
<a href="#" onClick={(e) => { e.preventDefault(); logout() }}>
  Log out
</a>
```

Good

```tsx
<button type="button" onClick={logout}>
  Log out
</button>
```

Excellent (explicit intent propagation; component emits intent, parent orchestrates)

```tsx
type Intent = { tag: "RequestLogout" }

type Props = { onIntent: (i: Intent) => void }

export function LogoutLink({ onIntent }: Props) {
  return (
    <button type="button" onClick={() => onIntent({ tag: "RequestLogout" })}>
      Log out
    </button>
  )
}
```

Reviewer notes:

* Components request; parents decide effects.

---

### C.3 Icon-only buttons (accessible name)

Bad (no accessible name; screen readers announce “button” only)

```tsx
<button type="button">
  <CloseIcon />
</button>
```

Good

```tsx
<button type="button" aria-label="Close">
  <CloseIcon aria-hidden="true" focusable="false" />
</button>
```

Excellent (SR-only text preferred when available)

```tsx
export function CloseButton() {
  return (
    <button type="button">
      <CloseIcon aria-hidden="true" focusable="false" />
      <span className="sr-only">Close</span>
    </button>
  )
}
```

---

### C.4 Controlled inputs: placeholder is not a label

Bad

```tsx
export function EmailField() {
  return <input type="email" placeholder="Email" />
}
```

Good

```tsx
export function EmailField() {
  return (
    <>
      <label htmlFor="email">Email</label>
      <input id="email" type="email" autoComplete="email" />
    </>
  )
}
```

Excellent (help text + stable association)

```tsx
export function EmailField() {
  return (
    <>
      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        autoComplete="email"
        aria-describedby="email-help"
      />
      <p id="email-help">We’ll only use this for account recovery.</p>
    </>
  )
}
```

Reviewer notes:

* `htmlFor`/`id` is not optional.

---

### C.5 Validation: visual error vs semantic error

Bad (red border only)

```tsx
export function EmailField({ error }: { error?: string }) {
  return (
    <div>
      <label>Email</label>
      <input className={error ? "error" : ""} />
      {error ? <div className="errorText">{error}</div> : null}
    </div>
  )
}
```

Good (`aria-invalid` + `aria-describedby`)

```tsx
export function EmailField({ error }: { error?: string }) {
  const errorId = error ? "email-error" : undefined

  return (
    <div>
      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        aria-invalid={Boolean(error)}
        aria-describedby={errorId}
      />
      {error ? <p id="email-error">{error}</p> : null}
    </div>
  )
}
```

Excellent (alert for immediate errors; use sparingly)

```tsx
export function EmailField({ error }: { error?: string }) {
  const errorId = error ? "email-error" : undefined

  return (
    <div>
      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        aria-invalid={Boolean(error)}
        aria-describedby={errorId}
      />
      {error ? (
        <p id="email-error" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  )
}
```

---

### C.6 “State in the DOM” via data attributes (dangerous drift)

Bad (DOM stores state; JS reads attributes to decide logic)

```tsx
export function Menu() {
  return (
    <div data-open="false" onClick={(e) => toggleFromDom(e.currentTarget)}>
      Menu
    </div>
  )
}
```

Good (state is in React; DOM reflects state)

```tsx
export function Menu() {
  const [open, setOpen] = React.useState(false)

  return (
    <>
      <button
        type="button"
        aria-expanded={open}
        aria-controls="menu"
        onClick={() => setOpen((x) => !x)}
      >
        Menu
      </button>

      <div id="menu" hidden={!open}>
        ...
      </div>
    </>
  )
}
```

Excellent (DOM is output artifact; state is explicit; props-driven for testability)

```tsx
type Props = { open: boolean; onToggle: () => void }

export function Menu({ open, onToggle }: Props) {
  return (
    <>
      <button
        type="button"
        aria-expanded={open}
        aria-controls="menu"
        onClick={onToggle}
      >
        Menu
      </button>

      <div id="menu" hidden={!open}>
        ...
      </div>
    </>
  )
}
```

---

### C.7 Preventing CSS-only meaning (“Schrödinger’s State”)

Bad (error state conveyed only by class)

```tsx
<div className={isError ? "banner banner-red" : "banner"}>
  Something went wrong
</div>
```

Good (semantic role)

```tsx
<div role="alert">
  Something went wrong
</div>
```

Excellent (typed state → semantic mapping; avoids raw strings in view logic)

```tsx
type Banner =
  | { tag: "None" }
  | { tag: "Error"; message: string }
  | { tag: "Info"; message: string }

export function BannerView({ banner }: { banner: Banner }) {
  switch (banner.tag) {
    case "None":
      return null

    case "Error":
      return <div role="alert">{banner.message}</div>

    case "Info":
      return <div role="status">{banner.message}</div>
  }
}
```

---

### C.8 `dangerouslySetInnerHTML` and untrusted HTML

Bad (potential XSS, breaks boundary discipline)

```tsx
export function Article({ html }: { html: string }) {
  return <div dangerouslySetInnerHTML={{ __html: html }} />
}
```

Good (render trusted structure, not raw HTML)

```tsx
export function Article({ paragraphs }: { paragraphs: string[] }) {
  return (
    <article>
      {paragraphs.map((p, i) => (
        <p key={i}>{p}</p>
      ))}
    </article>
  )
}
```

Excellent (explicit trust boundary + sanitization contract)

```tsx
type TrustedHtml = { __brand: "TrustedHtml"; value: string }

type Props = { html: TrustedHtml }

export function Article({ html }: Props) {
  return <div dangerouslySetInnerHTML={{ __html: html.value }} />
}
```

Reviewer notes:

* `dangerouslySetInnerHTML` is only acceptable behind an explicit “trusted” type/branding and a documented sanitization boundary.

---

### C.9 List rendering and keys (semantic + correctness)

Bad (index keys cause state corruption)

```tsx
{items.map((x, i) => (
  <Row key={i} item={x} />
))}
```

Good (stable key)

```tsx
{items.map((x) => (
  <Row key={x.id} item={x} />
))}
```

Excellent (semantic list markup, not div soup)

```tsx
<ul>
  {items.map((x) => (
    <li key={x.id}>
      <Row item={x} />
    </li>
  ))}
</ul>
```

---

### C.10 Dialogs / modals (semantics, focus, keyboard)

Bad (div-based modal, no semantics, escape key often broken)

```tsx
{open ? <div className="modal">...</div> : null}
```

Good (semantic role + labeled)

```tsx
{open ? (
  <div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
    <h2 id="dialog-title">Confirm</h2>
    ...
  </div>
) : null}
```

Excellent (close button has name; escape handling; focus management via library)

```tsx
type Props = { open: boolean; onClose: () => void }

export function ConfirmDialog({ open, onClose }: Props) {
  if (!open) return null

  return (
    <div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
      <h2 id="dialog-title">Confirm</h2>

      <button type="button" onClick={onClose}>
        <span className="sr-only">Close dialog</span>
        <CloseIcon aria-hidden="true" focusable="false" />
      </button>

      ...
    </div>
  )
}
```

Reviewer notes:

* In real systems, require a vetted dialog library (Radix, Reach, Ariakit) to guarantee focus trap and escape handling, but the semantic minimum must still be correct.

---

## Appendix D — JSX/TSX merge-blockers (review checklist)

A JSX/TSX PR fails review if any of the following are true:

1. Any interactive element is not a native interactive element (`button`, `a`, `input`, etc.) without a documented exception.
2. Any form control lacks an accessible name (`label`, `aria-label`, or SR-only text).
3. Visual error / expanded / checked state exists without semantic state (`aria-invalid`, `aria-expanded`, etc.).
4. DOM order differs from reading/keyboard order due to CSS reordering.
5. `dangerouslySetInnerHTML` is used without an explicit trusted-type boundary and sanitization contract.
6. Index keys are used for lists where items can reorder/insert/delete.
