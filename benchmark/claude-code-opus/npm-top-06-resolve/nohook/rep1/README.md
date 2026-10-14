# node-resolver

A dependency-free implementation of Node's CommonJS module resolution algorithm
(what `require.resolve()` does), written so a build tool can call it directly
and configure it.

It follows the pseudocode in the Node docs step by step:

- [CommonJS "All together"](https://nodejs.org/api/modules.html#all-together): core modules, relative/absolute paths, `node_modules` lookup, `main`, `index.*`
- [ESM resolution spec](https://nodejs.org/api/esm.html#resolution-algorithm-specification): `exports`, `imports`, conditions, subpath patterns, self-reference

## Usage

```js
import { resolve, Resolver } from 'node-resolver';

resolve('lodash/fp', '/project/src/app.js');
// → '/project/node_modules/lodash/fp.js'

// Reuse one instance across many lookups (it caches package.json reads).
const resolver = new Resolver({
  conditions: ['node', 'import'], // default: ['node', 'require']
  extensions: ['.js', '.json', '.node'],
  preserveSymlinks: false,
  paths: [], // extra global folders, like NODE_PATH
  fs: myVirtualFs, // optional: anything with statSync/readFileSync/realpathSync
});
resolver.resolve('#internal/utils', '/project/src/app.js');
```

Builtin modules are returned as given (`'fs'`, `'node:test'`). Errors use Node's
error codes (`MODULE_NOT_FOUND`, `ERR_PACKAGE_PATH_NOT_EXPORTED`,
`ERR_INVALID_PACKAGE_TARGET`, `ERR_INVALID_PACKAGE_CONFIG`,
`ERR_PACKAGE_IMPORT_NOT_DEFINED`, `ERR_INVALID_MODULE_SPECIFIER`).

## Layout

```
src/resolve.js   CommonJS algorithm (LOAD_AS_FILE, LOAD_NODE_MODULES, ...)
src/exports.js   "exports"/"imports" resolution (PACKAGE_EXPORTS_RESOLVE, ...)
src/errors.js    Errors with Node-compatible codes
test/            Tests that compare results against Node's real require.resolve
```

## Testing

```sh
npm test
```

Each test builds a fixture tree in a temp directory and checks that `resolve()`
gives the same path, or the same error code, as `createRequire(parent).resolve()`.
To cover a new case, add it to the fixture and the case list in `test/resolve.test.js`.

## Known gaps

- ESM-only resolution (`import` semantics: no extension probing, `file:` URL results) is not implemented. Only the `exports`/`imports` parts of the ESM spec are used.
- `require.extensions` hooks and `--experimental-*` loader flags are not modeled.
