# resolve-build-tool

Programmatic implementation of Node's CommonJS module resolution algorithm
(the same algorithm behind `require.resolve`), built on top of the
[`resolve`](https://www.npmjs.com/package/resolve) package.

## API

```ts
import { resolveModule, resolveModuleAsync, isCoreModule } from "resolve-build-tool";

// Sync, throws ModuleNotFoundError if unresolvable
const absPath = resolveModule("some-package", { basedir: __dirname });

// Async
const absPath2 = await resolveModuleAsync("./local-file", { basedir: __dirname });

// Core module check (fs, node:path, ...)
isCoreModule("fs"); // true
```

`ResolveOptions`:

- `basedir` (required) — directory to resolve from, as if a module lived there.
- `extensions` — file extensions to try when the specifier has none (default `[".js"]`).
- `moduleDirectory` — extra directory names to search besides `node_modules`.
- `preserveSymlinks` — mirrors `node --preserve-symlinks`.

## Scripts

```sh
npm run build       # compile src/ -> dist/
npm test            # run the test suite once
npm run test:watch  # run the test suite in watch mode
npm run dev         # run src/index.ts directly via tsx

```
