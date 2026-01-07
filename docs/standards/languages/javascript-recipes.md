# JavaScript Implementation Recipes (NON-NORMATIVE)

> **This document is INFORMATIVE.**
> It provides useful configuration baselines and recipes.
> For normative rules, see [javascript.md](javascript.md).

## A) Node-only baseline (service / CLI / library)

Recommended folders:

* `src/` for code
* `test/` for unit/integration tests

### A.1 package.json

```json
{
  "name": "your-project",
  "private": true,
  "type": "module",
  "engines": { "node": ">=20" },
  "scripts": {
    "fmt": "prettier --write .",
    "fmt:check": "prettier --check .",
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "typecheck": "tsc -p tsconfig.json --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "build": "node ./scripts/build.js",
    "check": "npm run fmt:check && npm run lint && npm run typecheck && npm run test && npm run build",
    "precommit": "node ./scripts/precommit.js"
  },
  "devDependencies": {
    "@eslint/js": "^9.0.0",
    "eslint": "^9.0.0",
    "globals": "^15.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0",
    "vitest": "^2.0.0"
  }
}
```

Notes:

* `build` is a placeholder; for many Node projects it can be `node -c` + smoke checks, or TS compilation if you’re using TS.
* Keep `typecheck` even for JS; use `allowJs` + `checkJs` (see tsconfig below).

### A.2 ESLint config (flat config)

Create `eslint.config.js`:

```js
import js from "@eslint/js";
import globals from "globals";

export default [
  js.configs.recommended,

  {
    files: ["**/*.{js,mjs,cjs}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.node
      }
    },
    rules: {
      "no-console": "off",
      "no-unused-vars": ["error", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
      "eqeqeq": ["error", "always"],
      "curly": ["error", "all"]
    }
  },

  {
    files: ["test/**/*.{js,mjs}"],
    languageOptions: {
      globals: {
        ...globals.node
      }
    },
    rules: {
      "no-unused-expressions": "off"
    }
  }
];
```

### A.3 Prettier config

Create `.prettierrc.json`:

```json
{
  "singleQuote": false,
  "semi": true,
  "trailingComma": "all"
}
```

### A.4 Type checking (works for JS and TS)

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "strict": true,
    "noEmit": true,

    "allowJs": true,
    "checkJs": true,

    "skipLibCheck": true
  },
  "include": ["src/**/*.js", "test/**/*.js", "src/**/*.ts", "test/**/*.ts"]
}
```

In JS files, enable local checking where you care:

```js
// @ts-check
```

### A.5 Precommit guard (clean tree + check)

Create `scripts/precommit.js`:

```js
import { execSync } from "node:child_process";

function sh(cmd) {
  execSync(cmd, { stdio: "inherit" });
}

function gitOutput(cmd) {
  return execSync(cmd, { encoding: "utf8" }).trim();
}

const status = gitOutput("git status --porcelain");
if (status.length !== 0) {
  console.error("Precommit failed: working tree is not clean.");
  process.exit(1);
}

sh("npm run check");
```

---

## B) React + Vite baseline (frontend)

### B.1 package.json

```json
{
  "name": "your-frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "fmt": "prettier --write .",
    "fmt:check": "prettier --check .",
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "typecheck": "tsc -p tsconfig.json --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "check": "npm run fmt:check && npm run lint && npm run typecheck && npm run test && npm run build"
  },
  "devDependencies": {
    "@eslint/js": "^9.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "eslint": "^9.0.0",
    "globals": "^15.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "vitest": "^2.0.0",
    "@vitejs/plugin-react": "^4.0.0"
  },
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```

### B.2 ESLint config (browser + React)

Create `eslint.config.js`:

```js
import js from "@eslint/js";
import globals from "globals";

export default [
  js.configs.recommended,

  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser
      }
    },
    rules: {
      "no-unused-vars": ["error", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
      "eqeqeq": ["error", "always"],
      "curly": ["error", "all"]
    }
  },

  {
    files: ["**/*.test.{js,jsx,ts,tsx}", "test/**/*.{js,jsx,ts,tsx}"],
    languageOptions: {
      globals: {
        ...globals.browser
      }
    }
  }
];
```

If you want React-specific linting (recommended), add:

* `eslint-plugin-react`
* `eslint-plugin-react-hooks`
  and extend rules. I did not include them above to keep the baseline minimal and version-agnostic; if you want the stricter set, say so and I will provide it as a drop-in.

### B.3 tsconfig.json (frontend)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

### B.4 Vitest config (optional but recommended)

Create `vitest.config.ts`:

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: false
  }
});
```

---

## C) Monorepo baseline (apps + packages)

This baseline assumes `pnpm` workspaces (cleanest lock + speed). You can adapt to npm/yarn, but do not mix.

Recommended layout:

```
.
├── package.json
├── pnpm-workspace.yaml
├── eslint.config.js
├── .prettierrc.json
├── tsconfig.base.json
├── apps/
│   ├── web/
│   └── api/
└── packages/
    ├── core/
    └── utils/
```

### C.1 Root package.json

```json
{
  "name": "your-monorepo",
  "private": true,
  "type": "module",
  "packageManager": "pnpm@9.0.0",
  "scripts": {
    "fmt": "prettier --write .",
    "fmt:check": "prettier --check .",
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "typecheck": "pnpm -r typecheck",
    "test": "pnpm -r test",
    "build": "pnpm -r build",
    "check": "pnpm run fmt:check && pnpm run lint && pnpm run typecheck && pnpm run test && pnpm run build"
  },
  "devDependencies": {
    "@eslint/js": "^9.0.0",
    "eslint": "^9.0.0",
    "globals": "^15.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0"
  }
}
```

### C.2 pnpm-workspace.yaml

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

### C.3 Root eslint.config.js (shared)

```js
import js from "@eslint/js";
import globals from "globals";

export default [
  js.configs.recommended,

  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.node,
        ...globals.browser
      }
    },
    rules: {
      "no-unused-vars": ["error", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
      "eqeqeq": ["error", "always"],
      "curly": ["error", "all"]
    }
  }
];
```

(You can tighten per-folder by adding overrides for `apps/web` vs `apps/api`, but this is a correct minimal shared baseline.)

### C.4 Root tsconfig.base.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true
  }
}
```

Each package/app then has its own `tsconfig.json` extending this base.

Example `packages/core/tsconfig.json`:

```json
{
  "extends": "../../tsconfig.base.json",
  "include": ["src"]
}
```

### C.5 Per-workspace scripts contract

Each workspace package **MUST** implement:

* `build`
* `test`
* `typecheck`

Example `packages/core/package.json`:

```json
{
  "name": "@your/core",
  "type": "module",
  "main": "./dist/index.js",
  "scripts": {
    "build": "node ./scripts/build.js",
    "test": "vitest run",
    "typecheck": "tsc -p tsconfig.json --noEmit"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vitest": "^2.0.0"
  }
}
```

---

## One policy decision you should make now

Do you want the baseline to be:

1. “JavaScript-first with `// @ts-check` + runtime schemas”, or
2. “TypeScript-first with strict mode everywhere”?

Both comply with your standard; (2) is typically easier to enforce at scale. If you state your preference, I will tighten the ESLint rules and provide the schema-validation baseline (Zod or equivalent) consistent with your “validate at boundaries” requirement.
