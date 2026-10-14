// Port of Node's CommonJS resolver (Module._resolveFilename and friends in
// lib/internal/modules/cjs/loader.js). The goal is byte-for-byte agreement
// with require.resolve() for the same filesystem, conditions and options.

import path from 'node:path';
import { isBuiltin } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createCachedFs, FILE, DIR } from './fs.js';
import { createEsmResolver, encodedSepRegEx } from './esm.js';
import {
  invalidArgType,
  invalidMainEntry,
  invalidModuleSpecifier,
  moduleNotFound,
} from './errors.js';

const DEFAULT_EXTENSIONS = ['.js', '.json', '.node'];

// Matches a bare package request: an optional @scope, the package name, and
// an optional "/subpath".
const EXPORTS_PATTERN = /^((?:@[^/\\%]+\/)?[^./\\%][^/\\%]*)(\/.*)?$/;

/**
 * The conditions require() uses in the running Node process: "require",
 * "node", "node-addons", plus "module-sync" where require(esm) is enabled.
 * ("default" always matches and doesn't need to be listed.)
 */
export function defaultConditions() {
  const conditions = ['require', 'node', 'node-addons'];
  if (process.features?.require_module) conditions.push('module-sync');
  return conditions;
}

/**
 * NODE_MODULES_PATHS: every ancestor `node_modules` directory of `from`, nearest
 * first, skipping directories that are themselves named node_modules.
 */
export function nodeModulesPaths(from) {
  const paths = [];
  for (let dir = path.resolve(from); ; ) {
    if (path.basename(dir) !== 'node_modules') paths.push(path.join(dir, 'node_modules'));
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return paths;
}

function isRelativeRequest(request) {
  if (request[0] !== '.') return false;
  if (request.length === 1) return true;
  const c = request[1];
  return c === '.' || c === '/' || (path.sep === '\\' && c === '\\');
}

// True for "x/", ".", "..", "x/." and "x/.." — requests Node will only try as
// directories, never as files.
function hasTrailingSlash(request) {
  const n = request.length;
  if (n === 0) return false;
  if (request[n - 1] === '/') return true;
  if (request[n - 1] !== '.') return false;
  if (n === 1 || request[n - 2] === '/') return true;
  return request[n - 2] === '.' && (n === 2 || request[n - 3] === '/');
}

/**
 * Normalises the "parent" argument the way createRequire() does: a path ending
 * in a separator is treated as a directory.
 */
function toParentPath(parent) {
  if (parent instanceof URL || (typeof parent === 'string' && parent.startsWith('file:'))) {
    parent = fileURLToPath(parent);
  }
  if (typeof parent !== 'string' || !path.isAbsolute(parent)) {
    throw invalidArgType('parent', 'an absolute path or file: URL', parent);
  }
  return parent.endsWith('/') || parent.endsWith(path.sep) ? path.join(parent, 'noop.js') : parent;
}

/**
 * @param {import('./index.d.ts').ResolverOptions} [options]
 */
export function createResolver(options = {}) {
  const fs = createCachedFs(options.fs);
  const extensions = options.extensions ?? DEFAULT_EXTENSIONS;
  const conditions = new Set(options.conditions ?? defaultConditions());
  const preserveSymlinks = options.preserveSymlinks ?? false;
  const globalPaths = options.globalPaths ?? [];
  const esm = createEsmResolver({ fs, conditions });

  function toRealPath(p) {
    return preserveSymlinks ? path.resolve(p) : fs.realpath(p);
  }

  function tryFile(p) {
    return fs.stat(p) === FILE ? toRealPath(p) : false;
  }

  function tryExtensions(base) {
    for (const ext of extensions) {
      const found = tryFile(base + ext);
      if (found) return found;
    }
    return false;
  }

  // LOAD_AS_DIRECTORY: package.json "main", falling back to index.
  function tryPackage(requestPath, originalRequest, parentPath) {
    const pkg = fs.readPackage(requestPath);
    const main = pkg?.data.main;
    if (typeof main !== 'string' || !main) {
      return tryExtensions(path.resolve(requestPath, 'index'));
    }
    const filename = path.resolve(requestPath, main);
    const found =
      tryFile(filename) ||
      tryExtensions(filename) ||
      tryExtensions(path.resolve(filename, 'index')) ||
      // Deprecated (DEP0128) but still honoured: a broken "main" falls back to index.
      tryExtensions(path.resolve(requestPath, 'index'));
    if (!found) throw invalidMainEntry(filename, originalRequest, parentPath);
    return found;
  }

  // Converts a URL produced by the ESM half into a real, existing file path.
  function finalizeEsmResolution(resolved, request, parentPath) {
    if (resolved.protocol === 'node:') return resolved.href;
    if (encodedSepRegEx.test(resolved.href)) {
      throw invalidModuleSpecifier(resolved.pathname, 'must not include encoded "/" or "\\" characters', parentPath);
    }
    const filename = fileURLToPath(resolved);
    const found = tryFile(filename);
    if (found) return found;
    throw moduleNotFound(request, parentPath);
  }

  function withEsmNotFound(request, parentPath, fn) {
    try {
      return fn();
    } catch (err) {
      if (err.code === 'ERR_MODULE_NOT_FOUND') throw moduleNotFound(request, parentPath);
      throw err;
    }
  }

  // LOAD_PACKAGE_EXPORTS for one node_modules directory.
  function resolveExports(nmPath, request, parentPath) {
    const match = EXPORTS_PATTERN.exec(request);
    if (!match) return false;
    const pkgPath = path.resolve(nmPath, match[1]);
    const pkg = fs.readPackage(pkgPath);
    if (pkg?.data.exports == null) return false;
    return withEsmNotFound(request, parentPath, () =>
      finalizeEsmResolution(
        esm.packageExportsResolve(pathToFileURL(pkg.path), '.' + (match[2] ?? ''), pkg.data.exports, pathToFileURL(parentPath)),
        request,
        parentPath,
      ));
  }

  // LOAD_PACKAGE_SELF: a package importing itself by name via its own "exports".
  function trySelf(parentPath, request) {
    const scope = fs.packageScope(path.dirname(parentPath));
    if (scope?.data.exports == null || typeof scope.data.name !== 'string') return false;
    const { name } = scope.data;
    let expansion;
    if (request === name) expansion = '.';
    else if (request.startsWith(`${name}/`)) expansion = '.' + request.slice(name.length);
    else return false;
    return withEsmNotFound(request, parentPath, () =>
      finalizeEsmResolution(
        esm.packageExportsResolve(pathToFileURL(scope.path), expansion, scope.data.exports, pathToFileURL(parentPath)),
        request,
        parentPath,
      ));
  }

  // LOAD_PACKAGE_IMPORTS. Returns false if the nearest package has no "imports"
  // field, in which case Node treats "#foo" as an ordinary bare specifier.
  function tryImports(parentPath, request) {
    const scope = fs.packageScope(path.dirname(parentPath));
    if (scope?.data.imports == null) return false;
    return withEsmNotFound(request, parentPath, () =>
      finalizeEsmResolution(esm.packageImportsResolve(request, pathToFileURL(parentPath)), request, parentPath));
  }

  function findPath(request, paths, parentPath) {
    const absoluteRequest = path.isAbsolute(request);
    const trailingSlash = hasTrailingSlash(request);

    for (const curPath of paths) {
      if (curPath && fs.stat(curPath) !== DIR) continue;

      if (!absoluteRequest) {
        const exported = resolveExports(curPath, request, parentPath);
        if (exported) return exported;
      }

      const basePath = path.resolve(curPath, request);
      const rc = fs.stat(basePath);
      let filename = false;
      if (!trailingSlash) {
        if (rc === FILE) filename = toRealPath(basePath);
        if (!filename) filename = tryExtensions(basePath);
      }
      if (!filename && rc === DIR) filename = tryPackage(basePath, request, parentPath);
      if (filename) return filename;
    }
    return false;
  }

  /** Directories that would be searched for `request` from `parent`. */
  function lookupPaths(request, parent) {
    const parentDir = path.dirname(toParentPath(parent));
    if (isRelativeRequest(request)) return [parentDir];
    if (path.isAbsolute(request)) return [''];
    return [...nodeModulesPaths(parentDir), ...globalPaths];
  }

  /**
   * Equivalent of createRequire(parent).resolve(request).
   * @param {string} request
   * @param {string | URL} parent absolute path (or file: URL) of the requiring module
   * @returns {string} absolute file path, or the specifier itself for builtins
   */
  function resolve(request, parent) {
    if (typeof request !== 'string') throw invalidArgType('request', 'string', request);
    if (isBuiltin(request)) return request;

    const parentPath = toParentPath(parent);

    if (request[0] === '#') {
      const imported = tryImports(parentPath, request);
      if (imported) return imported;
    }

    const self = trySelf(parentPath, request);
    if (self) return self;

    const filename = findPath(request, lookupPaths(request, parentPath), parentPath);
    if (filename) return filename;

    throw moduleNotFound(request, parentPath);
  }

  return {
    resolve,
    lookupPaths,
    /** Drop cached stat/realpath/package.json results (e.g. on file change). */
    clearCache: fs.clear,
  };
}

/** One-shot resolution with a fresh (uncached) resolver. */
export function resolve(request, parent, options) {
  return createResolver(options).resolve(request, parent);
}
