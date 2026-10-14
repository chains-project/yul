# node-module-resolver

A zero-dependency, programmatic implementation of Node.js's CommonJS module
resolution algorithm, i.e. what `require.resolve()` does, for use in build tools.

It follows the [documented algorithm](https://nodejs.org/api/modules.html#all-together):

1. Core modules (`fs`, `node:fs`, `node:test`, ...)
2. Relative/absolute paths: `LOAD_AS_FILE` (exact file, then `.js`/`.json`/`.node`), then `LOAD_AS_DIRECTORY` (`package.json` `"main"`, then `index.*`)
3. Package `"imports"` (`#internal`), including patterns and bare-package targets
4. Package self-reference by `"name"` via `"exports"`
5. `node_modules` hierarchy lookup with `"exports"` (conditions, subpath patterns, `null` exclusions, array fallbacks, target validation)

Results are realpath'd unless `preserveSymlinks` is set, just like Node.

## Usage

```js
import { createResolver } from 'node-module-resolver';

const resolver = createResolver({
  conditions: ['node', 'require'], // default: Node's CJS conditions (+ "module-sync" when require(esm) is on)
  extensions: ['.js', '.json', '.node'],
});

resolver.resolve('lodash/fp', '/path/to/project/src'); // -> absolute file path
resolver.resolve('node:fs', '/anywhere');              // -> 'node:fs'
resolver.clearCache();                                 // e.g. after file changes in watch mode
```

`basedir` is the *directory* of the requiring module (`path.dirname(parentFile)`).

### Options

| Option             | Default                       | Description                                                       |
| ------------------ | ----------------------------- | ----------------------------------------------------------------- |
| `fs`               | `node:fs`                     | Object with `statSync`, `readFileSync`, `realpathSync` (e.g. an in-memory fs) |
| `extensions`       | `['.js', '.json', '.node']`   | Extensions probed for extensionless requests, in order            |
| `conditions`       | `defaultConditions()`         | `"exports"`/`"imports"` conditions; `"default"` always matches    |
| `paths`            | `[]`                          | Extra folders searched after `node_modules` (like `NODE_PATH`)    |
| `preserveSymlinks` | `false`                       | Don't realpath results (like `--preserve-symlinks`)               |
| `builtins`         | `true`                        | Set `false` to resolve `fs` etc. through `node_modules` (browser bundling) |

Errors carry Node's codes: `MODULE_NOT_FOUND`, `ERR_PACKAGE_PATH_NOT_EXPORTED`,
`ERR_PACKAGE_IMPORT_NOT_DEFINED`, `ERR_INVALID_PACKAGE_TARGET`,
`ERR_INVALID_PACKAGE_CONFIG`, `ERR_INVALID_MODULE_SPECIFIER`.

The spec-level helpers `packageExportsResolve`, `packageImportsResolve`,
`patternKeyCompare` and `nodeModulesPaths` are exported too.

## Development

```sh
npm test   # node --test
```

The test suite builds a fixture tree in a temp directory and checks every case
against Node's real `require.resolve`, so differences from Node show up as
test failures.

Not implemented: the global folders (`$HOME/.node_modules`, `$PREFIX/lib/node`),
the `--preserve-symlinks-main` distinction, and deprecation warnings Node emits
for legacy configs.
