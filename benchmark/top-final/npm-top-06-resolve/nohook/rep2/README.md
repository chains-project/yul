# modres

A standalone, dependency-free implementation of Node's CommonJS module
resolution algorithm (the same one behind `require()` / `require.resolve()`),
for build tools that need to resolve specifiers to file paths without
spawning Node's own module loader.

## Usage

```js
const { resolve, ResolveError } = require('modres');

// Resolve relative to the file that would contain the require() call.
const target = resolve('./lib/foo', __filename);

// Resolve a bare specifier by walking up node_modules directories.
const dep = resolve('lodash', __filename);

try {
  resolve('missing-package', __filename);
} catch (err) {
  if (err instanceof ResolveError) {
    // err.code === 'MODULE_NOT_FOUND'
  }
}
```

`resolve(request, fromFile)` implements:

- `LOAD_AS_FILE` — exact file, then `.js`, `.json`, `.node`
- `LOAD_INDEX` — `index.js`, `index.json`, `index.node`
- `LOAD_AS_DIRECTORY` — a directory's `package.json#main`, falling back to its index
- `LOAD_NODE_MODULES` — walking up `node_modules` directories from `fromFile`

as documented in [Node's module docs](https://nodejs.org/api/modules.html#all-together).

## Test

```sh
npm test
```
