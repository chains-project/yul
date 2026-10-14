// Programmatic implementation of Node's CommonJS `require.resolve` algorithm:
// https://nodejs.org/api/modules.html#all-together
//
//   require(X) from module at path Y
//   1. If X is a core module, return X
//   2. If X begins with '/', set Y to the filesystem root
//   3. If X begins with './', '/' or '../': LOAD_AS_FILE(Y + X), LOAD_AS_DIRECTORY(Y + X)
//   4. If X begins with '#': LOAD_PACKAGE_IMPORTS(X, dirname(Y))
//   5. LOAD_PACKAGE_SELF(X, dirname(Y))
//   6. LOAD_NODE_MODULES(X, dirname(Y))
//   7. THROW "not found"

import nodeFs from 'node:fs';
import path from 'node:path';
import { isBuiltin } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { codedError, moduleNotFound } from './errors.js';
import { packageExportsResolve, packageImportsResolve } from './package-exports.js';

export const DEFAULT_EXTENSIONS = Object.freeze(['.js', '.json', '.node']);

/**
 * The conditions Node's CJS loader uses for "exports"/"imports".
 * "module-sync" is included when `require(esm)` is enabled in this process.
 */
export function defaultConditions() {
  const conditions = ['node', 'require'];
  if (process.features.require_module) conditions.push('module-sync');
  return conditions;
}

const STAT_MISSING = -1;
const STAT_FILE = 0;
const STAT_DIR = 1;

// Splits a bare specifier into package name and optional "/subpath".
const PACKAGE_NAME_RE = /^((?:@[^/\\%]+\/)?[^./\\%][^/\\%]*)(\/.*)?$/;
const RELATIVE_RE = /^\.\.?(?:[/\\]|$)/;
const ENCODED_SEPARATOR_RE = /%2f|%5c/i;

/**
 * NODE_MODULES_PATHS(START): every ancestor `node_modules` directory of
 * `from`, nearest first, skipping directories that are themselves named
 * `node_modules`.
 *
 * @param {string} from
 * @returns {string[]}
 */
export function nodeModulesPaths(from) {
  from = path.resolve(from);
  const { root } = path.parse(from);
  const parts = from.slice(root.length).split(path.sep).filter(Boolean);
  const dirs = [];
  for (let i = parts.length; i > 0; i--) {
    if (parts[i - 1] === 'node_modules') continue;
    dirs.push(path.join(root, ...parts.slice(0, i), 'node_modules'));
  }
  dirs.push(path.join(root, 'node_modules'));
  return dirs;
}

/**
 * Mirrors Node's trailing-slash detection: "x/", ".", "..", "x/." and "x/.."
 * may only resolve to a directory, never to a file.
 */
function hasTrailingSlash(request) {
  return /(?:^|\/)\.{0,2}$/.test(request) && request.length > 0;
}

function isRelativeOrAbsolute(request) {
  return RELATIVE_RE.test(request) || path.isAbsolute(request);
}

/**
 * @param {import('../types/index.d.ts').ResolverOptions} [options]
 * @returns {import('../types/index.d.ts').Resolver}
 */
export function createResolver(options = {}) {
  const {
    fs = nodeFs,
    extensions = DEFAULT_EXTENSIONS,
    conditions = defaultConditions(),
    paths: globalPaths = [],
    preserveSymlinks = false,
    builtins = true,
  } = options;

  const ctx = {
    conditions: new Set(conditions),
    resolveBare: (specifier, packageJsonUrl) => {
      const resolved = resolve(specifier, path.dirname(fileURLToPath(packageJsonUrl)));
      return path.isAbsolute(resolved) ? pathToFileURL(resolved) : new URL(resolved.startsWith('node:') ? resolved : `node:${resolved}`);
    },
  };

  const statCache = new Map();
  const realpathCache = new Map();
  const packageJsonCache = new Map();

  function stat(filename) {
    let result = statCache.get(filename);
    if (result === undefined) {
      try {
        const stats = fs.statSync(filename);
        result = stats.isDirectory() ? STAT_DIR : stats.isFile() ? STAT_FILE : STAT_MISSING;
      } catch {
        result = STAT_MISSING;
      }
      statCache.set(filename, result);
    }
    return result;
  }

  function toRealPath(filename) {
    if (preserveSymlinks) return filename;
    let real = realpathCache.get(filename);
    if (real === undefined) {
      real = fs.realpathSync(filename);
      realpathCache.set(filename, real);
    }
    return real;
  }

  /**
   * Reads `<dir>/package.json`. Returns null when it does not exist.
   * @returns {{ path: string, url: URL, data: Record<string, any> } | null}
   */
  function readPackageJson(dir) {
    const filename = path.join(dir, 'package.json');
    if (packageJsonCache.has(filename)) return packageJsonCache.get(filename);

    let result = null;
    if (stat(filename) === STAT_FILE) {
      let data;
      try {
        data = JSON.parse(fs.readFileSync(filename, 'utf8'));
      } catch (err) {
        throw codedError('ERR_INVALID_PACKAGE_CONFIG', `Invalid package config ${filename}: ${err.message}`);
      }
      if (typeof data !== 'object' || data === null) data = {};
      result = { path: filename, url: pathToFileURL(filename), data };
    }
    packageJsonCache.set(filename, result);
    return result;
  }

  /** LOOKUP_PACKAGE_SCOPE: nearest package.json, not crossing node_modules. */
  function readPackageScope(dir) {
    let current = dir;
    for (;;) {
      if (path.basename(current) === 'node_modules') return null;
      const pkg = readPackageJson(current);
      if (pkg) return pkg;
      const parent = path.dirname(current);
      if (parent === current) return null;
      current = parent;
    }
  }

  function tryFile(filename) {
    return stat(filename) === STAT_FILE ? toRealPath(filename) : undefined;
  }

  /** LOAD_AS_FILE steps 2-4 / LOAD_INDEX: X + each extension. */
  function tryExtensions(basePath) {
    for (const ext of extensions) {
      const found = tryFile(basePath + ext);
      if (found) return found;
    }
    return undefined;
  }

  /** LOAD_AS_DIRECTORY(X) */
  function tryPackage(dir, request, basedir) {
    const main = readPackageJson(dir)?.data.main;
    if (typeof main !== 'string' || main === '') {
      return tryExtensions(path.resolve(dir, 'index'));
    }

    const mainPath = path.resolve(dir, main);
    const found =
      tryFile(mainPath) ??
      tryExtensions(mainPath) ??
      tryExtensions(path.resolve(mainPath, 'index')) ??
      // Deprecated fallback: an invalid "main" falls back to the package's index.
      tryExtensions(path.resolve(dir, 'index'));
    if (found) return found;

    const err = moduleNotFound(request, basedir);
    err.message = `Cannot find module '${mainPath}'. Please verify that the package.json has a valid "main" entry`;
    err.path = path.join(dir, 'package.json');
    throw err;
  }

  /** LOAD_AS_FILE(X) then LOAD_AS_DIRECTORY(X). */
  function findPath(basePath, trailingSlash, request, basedir) {
    const rc = stat(basePath);
    if (!trailingSlash) {
      if (rc === STAT_FILE) return toRealPath(basePath);
      const found = tryExtensions(basePath);
      if (found) return found;
    }
    if (rc === STAT_DIR) return tryPackage(basePath, request, basedir);
    return undefined;
  }

  /** RESOLVE_ESM_MATCH(MATCH): the match must be an existing file; no extension probing. */
  function finalizeEsmMatch(url, request, basedir) {
    // An "imports" entry mapping to a builtin (`"#fs": "fs"`) works for ESM
    // `import`, but Node's CJS loader rejects it; mirror require.resolve.
    if (url.protocol !== 'file:') {
      throw codedError('ERR_INVALID_URL_SCHEME', 'The URL must be of scheme file', TypeError);
    }
    if (ENCODED_SEPARATOR_RE.test(url.pathname)) {
      throw codedError(
        'ERR_INVALID_MODULE_SPECIFIER',
        `Invalid module "${url.href}": must not include encoded "/" or "\\" characters`,
        TypeError,
      );
    }
    const found = tryFile(fileURLToPath(url));
    if (found) return found;
    throw moduleNotFound(request, basedir);
  }

  function withEsmNotFound(request, basedir, fn) {
    try {
      return fn();
    } catch (err) {
      if (err?.code === 'ERR_MODULE_NOT_FOUND') throw moduleNotFound(request, basedir);
      throw err;
    }
  }

  /** LOAD_PACKAGE_IMPORTS(X, DIR) */
  function resolveImports(request, basedir) {
    const pkg = readPackageScope(basedir);
    if (pkg?.data.imports == null) return undefined;
    return withEsmNotFound(request, basedir, () =>
      finalizeEsmMatch(packageImportsResolve(request, pkg.url, pkg.data.imports, ctx), request, basedir),
    );
  }

  /** LOAD_PACKAGE_SELF(X, DIR) */
  function resolveSelf(request, basedir) {
    const pkg = readPackageScope(basedir);
    if (!pkg || pkg.data.exports == null || typeof pkg.data.name !== 'string') return undefined;

    const { name, exports } = pkg.data;
    let subpath;
    if (request === name) subpath = '.';
    else if (request.startsWith(`${name}/`)) subpath = `.${request.slice(name.length)}`;
    else return undefined;

    return withEsmNotFound(request, basedir, () =>
      finalizeEsmMatch(packageExportsResolve(pkg.url, subpath, exports, ctx), request, basedir),
    );
  }

  /** LOAD_PACKAGE_EXPORTS(X, DIR) */
  function resolveExports(request, nodeModulesDir, basedir) {
    const match = PACKAGE_NAME_RE.exec(request);
    if (!match) return undefined;

    const pkg = readPackageJson(path.resolve(nodeModulesDir, match[1]));
    if (pkg?.data.exports == null) return undefined;

    return withEsmNotFound(request, basedir, () =>
      finalizeEsmMatch(
        packageExportsResolve(pkg.url, `.${match[2] ?? ''}`, pkg.data.exports, ctx),
        request,
        basedir,
      ),
    );
  }

  /**
   * Resolve `request` as if `require.resolve(request)` were called from a
   * module located in `basedir`.
   *
   * @param {string} request
   * @param {string} basedir Directory of the requiring module.
   * @returns {string} An absolute file path, or a builtin module id.
   */
  function resolve(request, basedir) {
    if (typeof request !== 'string' || request === '') {
      throw codedError('ERR_INVALID_ARG_VALUE', `The argument 'request' must be a non-empty string. Received ${JSON.stringify(request)}`, TypeError);
    }
    if (typeof basedir !== 'string') {
      throw codedError('ERR_INVALID_ARG_TYPE', `The "basedir" argument must be of type string. Received ${typeof basedir}`, TypeError);
    }
    basedir = path.resolve(basedir);

    // 1. Core modules. Like require.resolve (unlike require), an unknown
    // "node:" id is not an error here; it simply fails the lookup below.
    if (builtins && isBuiltin(request)) return request;

    const trailingSlash = hasTrailingSlash(request);

    // 2-3. Relative and absolute paths.
    if (isRelativeOrAbsolute(request)) {
      const found = findPath(path.resolve(basedir, request), trailingSlash, request, basedir);
      if (found) return found;
      throw moduleNotFound(request, basedir);
    }

    // 4. Package imports ("#internal").
    if (request.startsWith('#')) {
      const found = resolveImports(request, basedir);
      if (found) return found;
    }

    // 5. Package self-reference.
    const self = resolveSelf(request, basedir);
    if (self) return self;

    // 6. node_modules lookup (plus any extra global folders, like NODE_PATH).
    for (const dir of [...nodeModulesPaths(basedir), ...globalPaths]) {
      const viaExports = resolveExports(request, dir, basedir);
      if (viaExports) return viaExports;
      const found = findPath(path.resolve(dir, request), trailingSlash, request, basedir);
      if (found) return found;
    }

    // 7.
    throw moduleNotFound(request, basedir);
  }

  function clearCache() {
    statCache.clear();
    realpathCache.clear();
    packageJsonCache.clear();
  }

  return { resolve, clearCache };
}
