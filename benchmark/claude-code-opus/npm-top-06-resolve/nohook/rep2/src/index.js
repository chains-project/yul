// A programmatic implementation of Node's CommonJS resolution algorithm,
// following https://nodejs.org/api/modules.html#all-together and the
// behaviour of lib/internal/modules/cjs/loader.js.

import nodeFs from 'node:fs';
import path from 'node:path';
import { isBuiltin } from 'node:module';
import { createError, moduleNotFound } from './errors.js';
import { packageExportsResolve, packageImportsResolve } from './exports.js';

export { packageExportsResolve, packageImportsResolve, patternKeyCompare } from './exports.js';

const isWindows = path.sep === '\\';

// Matches "name" or "@scope/name" followed by an optional "/subpath".
// Same pattern Node uses to decide whether to consult "exports".
const EXPORTS_PATTERN = /^((?:@[^/\\%]+\/)?[^./\\%][^/\\%]*)(\/.*)?$/;

/**
 * @typedef {object} ResolverOptions
 * @property {Pick<typeof nodeFs, 'statSync' | 'readFileSync' | 'realpathSync'>} [fs]
 *   Filesystem implementation. Defaults to `node:fs`; pass e.g. memfs for a
 *   virtual filesystem.
 * @property {string[]} [conditions]  Export conditions. "default" is always
 *   active. Defaults to ["node", "require"].
 * @property {string[]} [extensions]  Extensions to try, in order. Defaults to
 *   [".js", ".json", ".node"].
 * @property {boolean} [preserveSymlinks]  Like `--preserve-symlinks`. When
 *   false (the default), results are passed through realpath.
 * @property {string[]} [paths]  Extra global lookup directories searched
 *   after the node_modules hierarchy (like NODE_PATH).
 * @property {(specifier: string) => boolean} [isBuiltin]  Decides which
 *   specifiers are core modules. Defaults to `module.isBuiltin`.
 */

/**
 * Create a resolver. Each resolver caches package.json reads; call
 * `clearCache()` when files on disk change (e.g. in watch mode).
 *
 * @param {ResolverOptions} [options]
 */
export function createResolver(options = {}) {
  const {
    fs = nodeFs,
    conditions = ['node', 'require'],
    extensions = ['.js', '.json', '.node'],
    preserveSymlinks = false,
    paths: globalPaths = [],
    isBuiltin: isBuiltinModule = isBuiltin,
  } = options;

  const conditionSet = new Set(conditions);
  /** @type {Map<string, object | null>} */
  const packageJsonCache = new Map();

  /** @returns {'file' | 'dir' | null} */
  function stat(p) {
    let st;
    try {
      st = fs.statSync(p, { throwIfNoEntry: false });
    } catch {
      return null;
    }
    if (!st) return null;
    if (st.isFile()) return 'file';
    if (st.isDirectory()) return 'dir';
    return null;
  }

  function isFile(p) {
    return stat(p) === 'file';
  }

  /** Read and cache `${dir}/package.json`; null when it doesn't exist. */
  function readPackageJson(dir) {
    if (packageJsonCache.has(dir)) return packageJsonCache.get(dir);

    const file = path.join(dir, 'package.json');
    let data = null;
    if (isFile(file)) {
      try {
        data = JSON.parse(fs.readFileSync(file, 'utf8'));
      } catch (err) {
        throw createError('ERR_INVALID_PACKAGE_CONFIG', `Invalid package config ${file}: ${err.message}`, {
          cause: err,
        });
      }
      if (data === null || typeof data !== 'object') data = {};
    }
    packageJsonCache.set(dir, data);
    return data;
  }

  /** LOOKUP_PACKAGE_SCOPE: nearest package.json, not crossing node_modules. */
  function findPackageScope(dir) {
    for (;;) {
      if (path.basename(dir) === 'node_modules') return null;
      const data = readPackageJson(dir);
      if (data) return { dir, data };
      const parent = path.dirname(dir);
      if (parent === dir) return null;
      dir = parent;
    }
  }

  function finalize(p) {
    return preserveSymlinks ? p : fs.realpathSync(p);
  }

  /** LOAD_AS_FILE */
  function loadAsFile(x) {
    if (isFile(x)) return x;
    for (const ext of extensions) {
      if (isFile(x + ext)) return x + ext;
    }
    return undefined;
  }

  /** LOAD_INDEX */
  function loadIndex(x) {
    for (const ext of extensions) {
      const candidate = path.join(x, `index${ext}`);
      if (isFile(candidate)) return candidate;
    }
    return undefined;
  }

  /** LOAD_AS_DIRECTORY */
  function loadAsDirectory(x, request, parent) {
    if (stat(x) !== 'dir') return undefined;

    const pkg = readPackageJson(x);
    if (pkg && typeof pkg.main === 'string' && pkg.main) {
      const m = path.resolve(x, pkg.main);
      const found = loadAsFile(m) ?? loadIndex(m) ?? loadIndex(x);
      if (found === undefined) {
        throw moduleNotFound(
          request,
          parent,
          `Cannot find module '${m}'. Please verify that the package.json has a valid "main" entry`,
        );
      }
      return found;
    }
    return loadIndex(x);
  }

  /** LOAD_AS_FILE then LOAD_AS_DIRECTORY, honouring trailing slashes. */
  function loadPath(base, trailingSlash, request, parent) {
    return (trailingSlash ? undefined : loadAsFile(base)) ?? loadAsDirectory(base, request, parent);
  }

  /** RESOLVE_ESM_MATCH: the target of exports/imports must exist as-is. */
  function resolveEsmMatch(p, request, parent) {
    if (isBuiltinModule(p)) return p;
    if (isFile(p)) return finalize(p);
    throw moduleNotFound(request, parent);
  }

  /** Resolves bare-specifier targets of "imports" entries. */
  function resolveBareTarget(specifier, pkgDir) {
    return resolve(specifier, path.join(pkgDir, 'package.json'));
  }

  /** LOAD_PACKAGE_IMPORTS */
  function loadPackageImports(request, dir, parent) {
    const scope = findPackageScope(dir);
    if (!scope || scope.data.imports == null) return undefined;
    const resolved = packageImportsResolve(scope.dir, request, scope.data.imports, conditionSet, resolveBareTarget);
    return resolveEsmMatch(resolved, request, parent);
  }

  /** LOAD_PACKAGE_SELF */
  function loadPackageSelf(request, dir, parent) {
    const scope = findPackageScope(dir);
    if (!scope || scope.data.exports == null || typeof scope.data.name !== 'string') return undefined;

    const { name } = scope.data;
    let subpath;
    if (request === name) subpath = '.';
    else if (request.startsWith(`${name}/`)) subpath = `.${request.slice(name.length)}`;
    else return undefined;

    const resolved = packageExportsResolve(scope.dir, subpath, scope.data.exports, conditionSet, resolveBareTarget);
    return resolveEsmMatch(resolved, request, parent);
  }

  /** LOAD_PACKAGE_EXPORTS */
  function loadPackageExports(request, nodeModulesDir, parent) {
    const match = EXPORTS_PATTERN.exec(request);
    if (!match) return undefined;
    const [, name, subpath = ''] = match;

    const pkgDir = path.resolve(nodeModulesDir, name);
    const pkg = readPackageJson(pkgDir);
    if (!pkg || pkg.exports == null) return undefined;

    const resolved = packageExportsResolve(pkgDir, `.${subpath}`, pkg.exports, conditionSet, resolveBareTarget);
    return resolveEsmMatch(resolved, request, parent);
  }

  /** LOAD_NODE_MODULES */
  function loadNodeModules(request, dir, trailingSlash, parent) {
    for (const nodeModulesDir of [...nodeModulesPaths(dir), ...globalPaths]) {
      const found =
        loadPackageExports(request, nodeModulesDir, parent) ??
        loadPath(path.resolve(nodeModulesDir, request), trailingSlash, request, parent);
      if (found !== undefined) return found;
    }
    return undefined;
  }

  /**
   * Resolve `request` as if `require.resolve(request)` were called from the
   * module at `parent`.
   *
   * @param {string} request  The specifier, e.g. "./foo", "lodash/fp", "#internal".
   * @param {string} parent   Absolute path of the requiring file. To resolve
   *   relative to a directory, pass a path to a (possibly nonexistent) file
   *   inside it, e.g. `path.join(dir, 'index.js')`.
   * @returns {string} Absolute file path, or the specifier itself for builtins.
   */
  function resolve(request, parent) {
    if (typeof request !== 'string') {
      throw createError('ERR_INVALID_ARG_TYPE', `The "request" argument must be of type string. Received ${typeof request}`);
    }
    if (typeof parent !== 'string' || !path.isAbsolute(parent)) {
      throw createError('ERR_INVALID_ARG_VALUE', `The "parent" argument must be an absolute path. Received ${parent}`);
    }

    // 1. Core modules.
    if (isBuiltinModule(request)) return request;
    if (request === '') throw moduleNotFound(request, parent);

    const dir = path.dirname(parent);
    const trailingSlash = hasTrailingSlash(request);

    // 2-3. Absolute and relative paths.
    if (path.isAbsolute(request) || isRelative(request)) {
      const found = loadPath(path.resolve(dir, request), trailingSlash, request, parent);
      if (found === undefined) throw moduleNotFound(request, parent);
      return finalize(found);
    }

    // 4. Package "imports" ("#specifier").
    if (request[0] === '#') {
      const found = loadPackageImports(request, dir, parent);
      if (found !== undefined) return found;
    }

    // 5. Self-reference via the package's own "exports".
    const self = loadPackageSelf(request, dir, parent);
    if (self !== undefined) return self;

    // 6. node_modules lookup.
    const found = loadNodeModules(request, dir, trailingSlash, parent);
    if (found === undefined) throw moduleNotFound(request, parent);
    // Exports results are already finalized; finalizing twice is harmless.
    return finalize(found);
  }

  return {
    resolve,
    nodeModulesPaths,
    clearCache() {
      packageJsonCache.clear();
    },
  };
}

/**
 * NODE_MODULES_PATHS: every `node_modules` directory from `dir` up to the
 * filesystem root, skipping directories that are themselves `node_modules`.
 */
export function nodeModulesPaths(dir) {
  dir = path.resolve(dir);
  const result = [];
  for (;;) {
    if (path.basename(dir) !== 'node_modules') {
      result.push(path.join(dir, 'node_modules'));
    }
    const parent = path.dirname(dir);
    if (parent === dir) return result;
    dir = parent;
  }
}

function isRelative(request) {
  if (request === '.' || request === '..') return true;
  if (request.startsWith('./') || request.startsWith('../')) return true;
  return isWindows && (request.startsWith('.\\') || request.startsWith('..\\'));
}

function hasTrailingSlash(request) {
  return (
    request === '.' ||
    request === '..' ||
    request.endsWith('/') ||
    request.endsWith('/.') ||
    request.endsWith('/..') ||
    (isWindows && (request.endsWith('\\') || request.endsWith('\\.') || request.endsWith('\\..')))
  );
}

const defaultResolver = createResolver();

/**
 * Resolve with default options (real filesystem, ["node", "require"]
 * conditions). Shares one package.json cache across calls.
 */
export function resolve(request, parent) {
  return defaultResolver.resolve(request, parent);
}
