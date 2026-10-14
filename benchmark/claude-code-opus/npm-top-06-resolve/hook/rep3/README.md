# node-module-resolver

A programmatic implementation of Node's CommonJS module resolution algorithm
(`require.resolve`) for build tools. It has zero dependencies and works with
any filesystem you plug in.

It covers the full algorithm from the [Node docs](https://nodejs.org/api/modules.html#all-together):

- builtins (`fs`, `node:fs`, scheme-only `node:test`)
- relative and absolute paths, with extension probing (`.js`, `.json`, `.node`)
- directories with `package.json` `main`, `index.*` fallback, and the DEP0128 fallback
- `node_modules` lookup up the directory tree
- package `"exports"`: subpaths, patterns, conditions, arrays, `null` exclusions, and sugar forms
- package `"imports"` (`#internal`), including bare-specifier targets
- package self-reference
- symlink realpath, with optional `preserveSymlinks`

## Usage

```js
import { Resolver } from 'node-module-resolver';

const resolver = new Resolver();
resolver.resolve('lodash/fp', '/repo/src/index.js'); // → '/repo/node_modules/lodash/fp.js'
resolver.resolve('fs', '/repo/src/index.js');        // → 'fs'
```

`parentPath` is the absolute path of the requiring file. If it ends with a
path separator, it is treated as a directory, the same way `createRequire` does.

### Options

| option             | default                                             | notes                                      |
| ------------------ | --------------------------------------------------- | ------------------------------------------ |
| `fs`               | `nodeFsHost` (real disk)                            | `{ stat, readFile, realpath }`; see `src/index.d.ts` |
| `extensions`       | `['.js', '.json', '.node']`                         | e.g. `['.ts', '.tsx', '.js']`              |
| `conditions`       | `['require', 'node']` + `'module-sync'` if supported | used by `exports` and `imports`            |
| `preserveSymlinks` | `false`                                             | like `--preserve-symlinks`                 |
| `paths`            | `[]`                                                | extra dirs searched last (like `NODE_PATH`) |

A `Resolver` caches parsed `package.json` files. Reuse one instance per build,
and call `clearCache()` when files change (for example, in watch mode).

Errors use Node's `code` values: `MODULE_NOT_FOUND`,
`ERR_PACKAGE_PATH_NOT_EXPORTED`, `ERR_PACKAGE_IMPORT_NOT_DEFINED`,
`ERR_INVALID_PACKAGE_TARGET`, `ERR_INVALID_PACKAGE_CONFIG`, and
`ERR_INVALID_MODULE_SPECIFIER`.

## Intentional differences from Node

- Global folders (`$HOME/.node_modules`, `$PREFIX/lib/node`, `NODE_PATH`) are
  not searched automatically. Pass them via `paths` if you need them.
- If an `"imports"` entry maps to a builtin (`"#fs": "fs"`), this returns `'fs'`.
  Node's CJS loader crashes on that case with `ERR_INVALID_URL_SCHEME`.
- `require.extensions` hooks and `Module._resolveFilename` patches are not
  consulted. Use the `extensions` option instead.
- Error messages are shorter than Node's (no "Require stack"), but the codes match.

## Development

```sh
npm test
```

`test/differential.test.js` builds a fixture tree in a temp directory. It
resolves each case with both Node's real `require.resolve` and this resolver,
and checks that the results (path or error code) are identical. To cover a new
edge case, add it to `test/fixtures.js` and the `cases` table.
