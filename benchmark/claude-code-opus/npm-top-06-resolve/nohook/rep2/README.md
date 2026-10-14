# node-module-resolve

A dependency-free, programmatic implementation of Node.js's CommonJS module
resolution algorithm (what `require.resolve` does), for use in build tools.

It follows the [documented algorithm](https://nodejs.org/api/modules.html#all-together)
and matches `lib/internal/modules/cjs/loader.js` behaviour, including:

- core modules (`fs`, `node:fs`, prefix-only modules like `node:test`)
- relative and absolute paths, extension probing, `index` files, trailing-slash semantics
- `package.json` `main` (including Node's deprecated fallback to `index`)
- `node_modules` hierarchy lookup and scoped packages
- `exports`: subpaths, conditions, conditional sugar, `*` patterns (most-specific wins),
  `null` exclusions, array fallbacks, and target validation
- `imports` (`#specifiers`), including mappings to other packages
- package self-reference
- symlink handling (`realpath` by default, or `preserveSymlinks`)

## Usage

```js
import { createResolver } from 'node-module-resolve';

const resolver = createResolver({
  conditions: ['node', 'require'], // "default" is always on
  extensions: ['.js', '.json', '.node'],
  preserveSymlinks: false,
  paths: [], // extra global lookup dirs, like NODE_PATH
  // fs: memfs, // any object with statSync / readFileSync / realpathSync
});

resolver.resolve('lodash/fp', '/project/src/index.js');
// → '/project/node_modules/lodash/fp.js'

resolver.resolve('fs', '/project/src/index.js'); // → 'fs'
```

The second argument is the **requiring file**, not a directory. To resolve
relative to a directory, pass a file path inside it, such as `path.join(dir, 'index.js')`
(the file doesn't need to exist).

Errors carry the same `code` values Node uses: `MODULE_NOT_FOUND`,
`ERR_PACKAGE_PATH_NOT_EXPORTED`, `ERR_PACKAGE_IMPORT_NOT_DEFINED`,
`ERR_INVALID_PACKAGE_TARGET`, `ERR_INVALID_PACKAGE_CONFIG` and
`ERR_INVALID_MODULE_SPECIFIER`.

Each resolver caches parsed `package.json` files. Call `resolver.clearCache()`
when they may have changed (e.g. in watch mode).

## Differences from `require.resolve`

- Global folders (`~/.node_modules`, `$PREFIX/lib/node`, `NODE_PATH`) are not
  searched unless passed via `paths`. This keeps builds reproducible.
- An `imports` entry that maps to a builtin (`"#fs": "fs"`) resolves to the
  builtin, as the ESM loader does. Node 22's CJS loader throws `ERR_INVALID_URL_SCHEME`.
- Bare-specifier targets in `imports` are resolved with CommonJS rules from the
  package root.
- The `parent` path is used as-is. Node's loader passes already-realpath'd filenames.

## Development

```sh
npm test
```

The test suite is differential: it builds a fixture tree on disk and asserts
that every case gives the same result, or the same error code, as Node's own
`createRequire(parent).resolve()`.
