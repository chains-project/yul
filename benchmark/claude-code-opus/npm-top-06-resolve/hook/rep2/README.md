# node-resolve-algo

A programmatic implementation of Node's CommonJS module resolution algorithm
(`require.resolve`), for build tools that need to resolve modules the way Node
does, with control over the filesystem, conditions, and caching.

It follows the [modules pseudocode](https://nodejs.org/api/modules.html#all-together)
and the [ESM spec](https://nodejs.org/api/esm.html#resolution-algorithm-specification)
for `exports` / `imports`.

```js
import { createResolver } from 'node-resolve-algo';

const resolver = createResolver({
  conditions: ['require', 'node', 'module-sync', 'node-addons'], // default
  extensions: ['.js', '.json', '.node'],                       // default
  preserveSymlinks: false,
});

resolver.resolve('lodash/fp', '/project/src/index.js');
// → { type: 'file', id: '/project/node_modules/lodash/fp.js' }
resolver.resolve('node:fs', '/project/src/index.js');
// → { type: 'builtin', id: 'node:fs' }

resolver.clearCache(); // after files change (watch mode)
```

Supported: core modules, relative/absolute paths, extension and `index` probing,
`package.json#main` (including the deprecated index fallback), `node_modules`
lookup, `exports` (subpaths, patterns, conditions, arrays, `null` exclusions),
`imports` (`#` specifiers, including mappings to other packages), package self-reference,
and symlink realpathing.

You can pass a custom `fs` (`{ stat, readFile, realpath }`) to resolve against
virtual or in-memory files.

## Layout

| File               | Role                                                         |
| ------------------ | ------------------------------------------------------------ |
| `src/resolve.js`   | Main CJS algorithm (LOAD_AS_FILE, LOAD_NODE_MODULES, …)      |
| `src/exports.js`   | `exports`/`imports` resolution (PACKAGE_TARGET_RESOLVE, …)   |
| `src/fs.js`        | Pluggable fs + memoised stat/package.json/realpath cache     |
| `src/errors.js`    | Errors with Node-compatible `code`s                          |

## Testing

```sh
npm test
```

The tests are **differential**: they build a fixture tree on disk and assert that each
request resolves to the same path, or fails with the same error `code`, as Node's
own `createRequire(from).resolve(request)`. To cover a new edge case, add a fixture
and a `[request, from]` row to `CASES` in `test/resolve.test.js`.

## Not (yet) implemented

- ESM `import` resolution (no extension probing, URL-based `import.meta.resolve` semantics)
- Default global folders (`$HOME/.node_modules`, `$PREFIX/lib/node`); use `globalPaths` instead
- Percent-decoding of `exports` targets, and `require.extensions` customisation
