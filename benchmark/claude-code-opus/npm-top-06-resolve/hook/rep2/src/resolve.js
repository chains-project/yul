/**
 * CommonJS module resolution, following the pseudocode in
 * https://nodejs.org/api/modules.html#all-together
 *
 *   require(X) from module at path Y
 *   1. If X is a core module, return it
 *   2. If X begins with '/', set Y to the filesystem root
 *   3. If X begins with './', '/' or '../': LOAD_AS_FILE(Y + X), LOAD_AS_DIRECTORY(Y + X)
 *   4. If X begins with '#': LOAD_PACKAGE_IMPORTS(X, dirname(Y))
 *   5. LOAD_PACKAGE_SELF(X, dirname(Y))
 *   6. LOAD_NODE_MODULES(X, dirname(Y))
 *   7. THROW "not found"
 */
import { isBuiltin } from 'node:module';
import path from 'node:path';
import { moduleNotFound } from './errors.js';
import { packageExportsResolve, packageImportsResolve } from './exports.js';
import { createCachedFs, defaultFs } from './fs.js';

/** Conditions Node uses for `require()` (Node >= 22.12 with require(esm) on). */
export const DEFAULT_CONDITIONS = Object.freeze(['require', 'node', 'module-sync', 'node-addons']);

/** Extension probing order for LOAD_AS_FILE / LOAD_INDEX. */
export const DEFAULT_EXTENSIONS = Object.freeze(['.js', '.json', '.node']);

/**
 * @typedef {object} ResolverOptions
 * @property {readonly string[]} [conditions]  Export conditions ("default" always matches).
 * @property {readonly string[]} [extensions]  Extensions probed for extensionless requests.
 * @property {boolean} [preserveSymlinks]      Like `--preserve-symlinks`: skip realpath on results.
 * @property {readonly string[]} [globalPaths] Extra lookup dirs after node_modules (like NODE_PATH).
 * @property {import('./fs.js').ResolverFs} [fs]
 */

/**
 * @typedef {object} Resolution
 * @property {'builtin' | 'file'} type
 * @property {string} id  Builtin name (e.g. "fs", "node:test") or absolute file path.
 */

/**
 * Creates a reusable resolver with its own filesystem cache.
 *
 * @param {ResolverOptions} [options]
 */
export function createResolver(options = {}) {
  const conditions = new Set(options.conditions ?? DEFAULT_CONDITIONS);
  const extensions = options.extensions ?? DEFAULT_EXTENSIONS;
  const preserveSymlinks = options.preserveSymlinks ?? false;
  const globalPaths = options.globalPaths ?? [];
  const fs = createCachedFs(options.fs ?? defaultFs);

  /**
   * Resolve `request` as if `require(request)` were called from the file `from`.
   *
   * @param {string} request
   * @param {string} from  Absolute path of the importing file.
   * @returns {Resolution}
   */
  function resolve(request, from) {
    if (isBuiltin(request)) return { type: 'builtin', id: request };

    const fromDir = path.dirname(from);
    const found = resolveFile(request, fromDir);
    if (found === null) throw moduleNotFound(request, from);
    return { type: 'file', id: preserveSymlinks ? found : fs.realpath(found) };
  }

  /**
   * @param {string} request
   * @param {string} fromDir
   * @returns {string | null}
   */
  function resolveFile(request, fromDir) {
    if (isRelativeOrAbsolute(request)) {
      const target = path.resolve(fromDir, request);
      // A trailing slash means "directory only" (require('./dir/')).
      if (!/[\\/]$/.test(request) && !/(^|[\\/])\.\.?$/.test(request)) {
        const file = loadAsFile(target);
        if (file) return file;
      }
      return loadAsDirectory(target);
    }

    if (request.startsWith('#')) {
      const scope = fs.findPackageScope(fromDir);
      if (scope && scope.imports != null) {
        const result = packageImportsResolve(request, scope, conditions);
        return result.type === 'bare'
          ? resolveFile(result.specifier, scope.dir)
          : resolveEsmMatch(result.path);
      }
      // No "imports" field: fall through and treat it as a package name.
    }

    const self = loadPackageSelf(request, fromDir);
    if (self) return self;

    return loadNodeModules(request, fromDir);
  }

  /**
   * LOAD_AS_FILE(X)
   * @param {string} x
   */
  function loadAsFile(x) {
    if (fs.isFile(x)) return x;
    for (const ext of extensions) {
      if (fs.isFile(x + ext)) return x + ext;
    }
    return null;
  }

  /**
   * LOAD_INDEX(X)
   * @param {string} x
   */
  function probeIndex(x) {
    for (const ext of extensions) {
      const p = path.join(x, 'index' + ext);
      if (fs.isFile(p)) return p;
    }
    return null;
  }

  /**
   * LOAD_AS_DIRECTORY(X)
   * @param {string} x
   */
  function loadAsDirectory(x) {
    const pkg = fs.readPackageJson(x);
    if (pkg?.main) {
      const m = path.resolve(x, pkg.main);
      const found = loadAsFile(m) ?? probeIndex(m) ?? probeIndex(x); // last one is deprecated (DEP0128)
      if (found) return found;
      throw moduleNotFound(m, pkg.path);
    }
    return probeIndex(x);
  }

  /**
   * LOAD_NODE_MODULES(X, START)
   * @param {string} request
   * @param {string} start
   */
  function loadNodeModules(request, start) {
    if (request === '') return null;
    for (const dir of nodeModulesPaths(start)) {
      const found = loadPackageExports(request, dir) ?? loadAsFileOrDirectory(path.join(dir, request));
      if (found) return found;
    }
    for (const dir of globalPaths) {
      const found = loadAsFileOrDirectory(path.join(dir, request));
      if (found) return found;
    }
    return null;
  }

  /** @param {string} x */
  function loadAsFileOrDirectory(x) {
    return loadAsFile(x) ?? (fs.isDir(x) ? loadAsDirectory(x) : null);
  }

  /**
   * LOAD_PACKAGE_EXPORTS(X, DIR)
   * @param {string} request
   * @param {string} dir  A node_modules directory.
   */
  function loadPackageExports(request, dir) {
    const parsed = parsePackageName(request);
    if (!parsed) return null;
    const pkg = fs.readPackageJson(path.join(dir, parsed.name));
    if (!pkg || pkg.exports == null) return null;
    const result = packageExportsResolve(pkg, '.' + parsed.subpath, conditions);
    return resolveEsmMatch(/** @type {{ path: string }} */ (result).path);
  }

  /**
   * LOAD_PACKAGE_SELF(X, DIR): a package may require itself by name via "exports".
   * @param {string} request
   * @param {string} dir
   */
  function loadPackageSelf(request, dir) {
    const scope = fs.findPackageScope(dir);
    if (!scope || scope.exports == null || !scope.name) return null;
    if (request !== scope.name && !request.startsWith(scope.name + '/')) return null;
    const result = packageExportsResolve(scope, '.' + request.slice(scope.name.length), conditions);
    return resolveEsmMatch(/** @type {{ path: string }} */ (result).path);
  }

  /**
   * RESOLVE_ESM_MATCH: exports/imports targets are exact - no extension probing.
   * @param {string} p
   */
  function resolveEsmMatch(p) {
    if (fs.isFile(p)) return p;
    throw moduleNotFound(p, p);
  }

  return {
    resolve,
    /** Drop cached filesystem state (call when files change in watch mode). */
    clearCache: fs.clear,
  };
}

/**
 * NODE_MODULES_PATHS(START)
 *
 * @param {string} start
 * @returns {string[]}
 */
export function nodeModulesPaths(start) {
  const dirs = [];
  let current = path.resolve(start);
  for (;;) {
    if (path.basename(current) !== 'node_modules') dirs.push(path.join(current, 'node_modules'));
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return dirs;
}

/**
 * Splits "pkg/sub" or "@scope/pkg/sub" into name and "/sub" subpath.
 *
 * @param {string} request
 * @returns {{ name: string, subpath: string } | null}
 */
export function parsePackageName(request) {
  const match = /^((?:@[^/\\%]+\/)?[^./\\%@][^/\\%]*)(\/.*)?$/.exec(request);
  if (!match) return null;
  return { name: match[1], subpath: match[2] ?? '' };
}

/** @param {string} request */
function isRelativeOrAbsolute(request) {
  return (
    request === '.' ||
    request === '..' ||
    request.startsWith('./') ||
    request.startsWith('../') ||
    path.isAbsolute(request) ||
    (path.sep === '\\' && (request.startsWith('.\\') || request.startsWith('..\\')))
  );
}
