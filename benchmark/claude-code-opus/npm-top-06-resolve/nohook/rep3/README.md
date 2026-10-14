# node-module-resolver

A programmatic, zero-dependency implementation of Node's CommonJS module
resolution algorithm — what `require.resolve()` does — for use in build tools.

It is a direct port of `Module._resolveFilename` (and the parts of Node's ESM
resolver it calls for `"exports"` / `"imports"`). It adds a pluggable
filesystem, caching, and configurable conditions/extensions.

## Usage

```js
import { createResolver } from 'node-module-resolver';

const resolver = createResolver({
  // all optional:
  conditions: ['require', 'node'],     // default: what require() uses in this Node
  extensions: ['.js', '.json', '.node'],
  preserveSymlinks: false,
  globalPaths: [],                     // NODE_PATH-style fallback directories
  fs: memfs,                           // anything with statSync/readFileSync/realpathSync
});

resolver.resolve('lodash/fp', '/project/src/index.js');
// => '/project/node_modules/lodash/fp.js'

resolver.resolve('fs', '/project/src/index.js');       // => 'fs' (builtins pass through)
resolver.lookupPaths('lodash', '/project/src/index.js'); // node_modules search order
resolver.clearCache();                                  // after files change (watch mode)
```

`parent` is the absolute path (or `file:` URL) of the requiring module. Like
`createRequire()`, a path ending in `/` is treated as a directory.

Errors carry the same `code` as Node's: `MODULE_NOT_FOUND`,
`ERR_PACKAGE_PATH_NOT_EXPORTED`, `ERR_PACKAGE_IMPORT_NOT_DEFINED`,
`ERR_INVALID_PACKAGE_TARGET`, `ERR_INVALID_PACKAGE_CONFIG`,
`ERR_INVALID_MODULE_SPECIFIER`.

## What's implemented

Following the [algorithm in the Node docs](https://nodejs.org/api/modules.html#all-together):

- core modules (`fs`, `node:fs`, prefix-only modules like `node:test`)
- `LOAD_AS_FILE` / `LOAD_AS_DIRECTORY`: extension probing, `index.*`,
  `package.json` `"main"` (including the deprecated fallback to `index` when `"main"` is broken)
- trailing-slash requests (`./dir/`, `.`, `..`), which skip file probing
- `LOAD_PACKAGE_IMPORTS` (`#internal`), including bare-specifier targets
- `LOAD_PACKAGE_SELF` (a package requiring itself by name)
- `LOAD_NODE_MODULES` with `LOAD_PACKAGE_EXPORTS`: subpaths, `*` patterns
  ranked by specificity, conditions, arrays/fallbacks, `null` exclusions, and the same
  validation of invalid segments, path escapes and encoded separators
- realpath-ing of results (or `preserveSymlinks`)

### Intentional differences

- An `"imports"` entry that maps to a builtin (`"#fs": "fs"`) resolves to
  `'node:fs'`. Node's `require.resolve` throws `ERR_INVALID_URL_SCHEME` here.
- `globalPaths` defaults to `[]` rather than Node's `NODE_PATH`/`~/.node_modules`,
  so builds don't depend on the machine they run on. Pass
  `createRequire(import.meta.url)('module').globalPaths` to opt in.

## Development

```sh
npm test
```

`test/differential.test.js` builds a fixture tree and resolves every case both
with this library and with Node's own `createRequire(parent).resolve()`. The
two must agree on the resolved path or the error code. To cover a new edge
case, add a fixture entry and a `[parent, request]` row.

Requires Node ≥ 22 (the default conditions are taken from the running process,
including `module-sync` when `require(esm)` is enabled).
