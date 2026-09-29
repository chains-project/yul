# node-module-resolver

A zero-dependency, programmatic implementation of Node.js module resolution
(the algorithm behind `require.resolve`) for use in build tools, bundlers,
linters, and codegen.

It implements the CommonJS resolution algorithm plus modern package entry
points:

- `LOAD_AS_FILE` / `LOAD_INDEX` / `LOAD_AS_DIRECTORY`
- `node_modules` directory walking (nested, scoped, `NODE_PATH`-style search)
- `package.json` `main` (including directories and extension/index fallback)
- `exports` field: conditions, subpaths, `*` patterns, and fallback arrays
- `imports` field (`#specifiers`) resolved against the package scope
- Core modules (`fs`, `node:path`, ...)
- `preserveSymlinks` behavior and a package.json parse cache

The test suite is differentially checked against Node's own `require.resolve`.

## Install

```sh
npm install node-module-resolver
```

Requires Node.js 18+.

## Usage

```js
import { resolveSync, createResolver } from 'node-module-resolver';

resolveSync('./src/index.js', { basedir: process.cwd() });
// => '/abs/path/to/src/index.js'

resolveSync('some-package/feature', {
  basedir: process.cwd(),
  conditions: ['node', 'import'],
});

const resolver = createResolver({ extensions: ['.ts', '.js'], conditions: ['node', 'require'] });
resolver.resolve('./entry', '/abs/project');
```

Async form:

```js
import { resolve } from 'node-module-resolver';
const file = await resolve('some-package', { basedir: process.cwd() });
```

### Options

| Option             | Default                | Description                                             |
| ------------------ | ---------------------- | ------------------------------------------------------- |
| `basedir`          | `process.cwd()`        | Base directory for relative and bare specifiers.        |
| `extensions`       | `['.js', '.json', '.node']` | Extensions tried in order.                        |
| `conditions`       | `['node', 'require']`  | Conditions applied to `exports`/`imports`.              |
| `preserveSymlinks` | `false`                | When `false`, resolved paths are realpath'd.            |

### Errors

Errors carry a `code` matching Node's conventions:

- `MODULE_NOT_FOUND`
- `ERR_PACKAGE_PATH_NOT_EXPORTED`
- `ERR_PACKAGE_IMPORT_NOT_DEFINED`
- `ERR_INVALID_MODULE_SPECIFIER`
- `ERR_INVALID_PACKAGE_CONFIG`

```js
import { resolveSync, ModuleNotFoundError } from 'node-module-resolver';

try {
  resolveSync('missing-pkg', { basedir: process.cwd() });
} catch (error) {
  if (error instanceof ModuleNotFoundError) {
    console.error(error.request, error.paths);
  }
}
```

## CLI

```sh
node bin/resolve.js --basedir ./app some-package ./relative
node bin/resolve.js -c node,import some-package/feature
```

## API surface

- `resolveSync(request, options?)` - synchronous resolve.
- `resolve(request, options?)` - promise wrapper around `resolveSync`.
- `createResolver(options?)` - reusable `Resolver` instance.
- `Resolver` - class with `resolve(request, basedir?)` and `readPackageJson()`.
- `isCoreModule`, `nodeModulesPaths`, `parsePackageSpecifier` - helpers.
- Error classes listed above.

## Development

```sh
npm test          # node --test
npm run test:watch
```

## License

MIT
