/**
 * Node's CommonJS resolution algorithm, i.e. what `require.resolve()` does.
 *
 * Mirrors the pseudocode at https://nodejs.org/api/modules.html#all-together
 * Each step function below is named after the matching step in that document.
 */
import nodeFs from 'node:fs';
import path from 'node:path';
import { isBuiltin } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { invalidModuleSpecifier, invalidPackageConfig, moduleNotFound } from './errors.js';
import { packageExportsResolve, packageImportsResolve } from './exports.js';

export const DEFAULT_EXTENSIONS = Object.freeze(['.js', '.json', '.node']);
export const DEFAULT_CONDITIONS = Object.freeze(['node', 'require']);

// "name" or "@scope/name", followed by an optional "/subpath".
const packageNameRegEx = /^((?:@[^/\\%]+\/)?[^./\\%][^/\\%]*)(\/.*)?$/;

/**
 * @typedef {object} ResolveOptions
 * @property {string[]} [extensions]     Extensions to try, in order. Default: ['.js', '.json', '.node']
 * @property {string[]} [conditions]     Conditions for "exports"/"imports". Default: ['node', 'require']
 * @property {boolean} [preserveSymlinks] Same as `node --preserve-symlinks`. Default: false
 * @property {string[]} [paths]          Extra folders to search after node_modules (like NODE_PATH).
 * @property {typeof nodeFs} [fs]        A custom fs implementation (needs statSync, readFileSync, realpathSync).
 */

/**
 * Resolve `request` the way `require.resolve(request)` would when called from `parentPath`.
 *
 * @param {string} request     The specifier passed to require().
 * @param {string} parentPath  Absolute path of the requiring file.
 * @param {ResolveOptions} [options]
 * @returns {string} An absolute file path, or the name of a builtin module.
 */
export function resolve(request, parentPath, options = {}) {
  if (typeof request !== 'string' || request === '') {
    throw new TypeError('request must be a non-empty string');
  }
  const resolver = new Resolver(options);
  return resolver.resolve(request, path.resolve(parentPath));
}

/**
 * Reusable resolver. Caches package.json reads, so create a new instance
 * (or call `clearCache()`) when files on disk change.
 */
export class Resolver {
  /** @param {ResolveOptions} [options] */
  constructor(options = {}) {
    this.fs = options.fs ?? nodeFs;
    this.extensions = options.extensions ?? DEFAULT_EXTENSIONS;
    this.conditions = options.conditions ?? DEFAULT_CONDITIONS;
    this.preserveSymlinks = options.preserveSymlinks ?? false;
    this.globalPaths = options.paths ?? [];
    this.packageJsonCache = new Map();
  }

  clearCache() {
    this.packageJsonCache.clear();
  }

  /**
   * @param {string} request
   * @param {string} parentPath Absolute path of the requiring file.
   * @returns {string}
   */
  resolve(request, parentPath) {
    // 1. Core modules.
    if (isBuiltin(request)) return request;

    const parentDir = path.dirname(parentPath);
    const fail = () => moduleNotFound(request, parentPath);

    // 2-3. Relative or absolute paths.
    if (isRelative(request) || path.isAbsolute(request)) {
      const target = path.resolve(parentDir, request);
      const found = this.loadPath(target, hasTrailingSlash(request), fail);
      if (found) return this.finalize(found);
      throw fail();
    }

    // 4. Package imports ("#name"). Without an "imports" field, Node falls through.
    if (request.startsWith('#')) {
      const imported = this.loadPackageImports(request, parentDir, fail);
      if (imported) return imported;
    }

    // 5. Self-reference by package name.
    const self = this.loadPackageSelf(request, parentDir, fail);
    if (self) return self;

    // 6. node_modules lookup.
    const found = this.loadNodeModules(request, parentDir, fail);
    if (found) return found;

    // 7.
    throw fail();
  }

  /** LOAD_AS_FILE then LOAD_AS_DIRECTORY. A trailing slash skips the file step. */
  loadPath(target, directoryOnly, fail) {
    if (!directoryOnly) {
      const file = this.loadAsFile(target);
      if (file) return file;
    }
    if (this.isDirectory(target)) return this.loadAsDirectory(target, fail);
    return undefined;
  }

  loadAsFile(target) {
    if (this.isFile(target)) return target;
    for (const ext of this.extensions) {
      if (this.isFile(target + ext)) return target + ext;
    }
    return undefined;
  }

  loadIndex(dir) {
    for (const ext of this.extensions) {
      const file = path.join(dir, 'index' + ext);
      if (this.isFile(file)) return file;
    }
    return undefined;
  }

  loadAsDirectory(dir, fail) {
    const pkg = this.readPackageJson(dir);
    const main = pkg?.main;
    if (typeof main === 'string' && main !== '') {
      const mainPath = path.resolve(dir, main);
      const found =
        this.loadAsFile(mainPath) ??
        this.loadIndex(mainPath) ??
        // Deprecated in Node (DEP0128), but still supported.
        this.loadIndex(dir);
      if (found) return found;
      const err = fail();
      err.message += `. Please verify that ${path.join(dir, 'package.json')} has a valid "main" entry`;
      throw err;
    }
    return this.loadIndex(dir);
  }

  loadNodeModules(request, startDir, fail) {
    const dirs = [...nodeModulesPaths(startDir), ...this.globalPaths];
    const directoryOnly = hasTrailingSlash(request);
    for (const dir of dirs) {
      const exported = this.loadPackageExports(request, dir, fail);
      if (exported) return exported;
      const found = this.loadPath(path.resolve(dir, request), directoryOnly, fail);
      if (found) return this.finalize(found);
    }
    return undefined;
  }

  loadPackageExports(request, nodeModulesDir, fail) {
    const match = packageNameRegEx.exec(request);
    if (!match) return undefined;
    const [, name, subpath = ''] = match;
    const pkgDir = path.resolve(nodeModulesDir, name);
    const pkg = this.readPackageJson(pkgDir);
    if (pkg?.exports == null) return undefined;

    const url = packageExportsResolve(pkgDir, '.' + subpath, pkg.exports, this.conditions);
    return this.resolveEsmMatch(url, fail);
  }

  loadPackageSelf(request, dir, fail) {
    const scope = this.findPackageScope(dir);
    if (!scope) return undefined;
    const { dir: pkgDir, pkg } = scope;
    if (pkg.exports == null || typeof pkg.name !== 'string') return undefined;
    if (request !== pkg.name && !request.startsWith(pkg.name + '/')) return undefined;

    const subpath = '.' + request.slice(pkg.name.length);
    const url = packageExportsResolve(pkgDir, subpath, pkg.exports, this.conditions);
    return this.resolveEsmMatch(url, fail);
  }

  loadPackageImports(request, dir, fail) {
    const scope = this.findPackageScope(dir);
    if (scope?.pkg.imports == null) return undefined;
    const { dir: pkgDir, pkg } = scope;

    // Bare targets ("#dep": "some-package") resolve as if required from the package root.
    const resolveBare = (specifier) => {
      const resolved = this.resolve(specifier, path.join(pkgDir, 'package.json'));
      return isBuiltin(resolved) ? resolved : pathToFileURL(resolved);
    };
    const resolved = packageImportsResolve(request, pkgDir, pkg.imports, this.conditions, resolveBare);
    return this.resolveEsmMatch(resolved, fail);
  }

  /** RESOLVE_ESM_MATCH: exports/imports targets are exact; no extension probing. */
  resolveEsmMatch(resolved, fail) {
    if (typeof resolved === 'string') return resolved;
    if (/%2f|%5c/i.test(resolved.pathname)) {
      throw invalidModuleSpecifier(resolved.pathname, 'must not include encoded "/" or "\\" characters');
    }
    const file = fileURLToPath(resolved);
    if (this.isFile(file)) return this.finalize(file);
    throw fail();
  }

  /** LOOKUP_PACKAGE_SCOPE: nearest package.json, without crossing a node_modules boundary. */
  findPackageScope(startDir) {
    let dir = startDir;
    while (true) {
      if (path.basename(dir) === 'node_modules') return undefined;
      const pkg = this.readPackageJson(dir);
      if (pkg) return { dir, pkg };
      const parent = path.dirname(dir);
      if (parent === dir) return undefined;
      dir = parent;
    }
  }

  readPackageJson(dir) {
    const file = path.join(dir, 'package.json');
    if (this.packageJsonCache.has(file)) return this.packageJsonCache.get(file);

    let pkg = null;
    let source;
    try {
      source = this.fs.readFileSync(file, 'utf8');
    } catch (err) {
      if (err.code !== 'ENOENT' && err.code !== 'ENOTDIR' && err.code !== 'EISDIR') throw err;
    }
    if (source !== undefined) {
      try {
        pkg = JSON.parse(source);
      } catch (err) {
        throw invalidPackageConfig(file, err.message);
      }
      if (pkg === null || typeof pkg !== 'object') pkg = {};
    }
    this.packageJsonCache.set(file, pkg);
    return pkg;
  }

  finalize(file) {
    return this.preserveSymlinks ? file : this.fs.realpathSync(file);
  }

  isFile(file) {
    return this.fs.statSync(file, { throwIfNoEntry: false })?.isFile() ?? false;
  }

  isDirectory(file) {
    return this.fs.statSync(file, { throwIfNoEntry: false })?.isDirectory() ?? false;
  }
}

/** NODE_MODULES_PATHS: every ancestor's node_modules, skipping node_modules/node_modules. */
export function nodeModulesPaths(startDir) {
  const dirs = [];
  let dir = path.resolve(startDir);
  while (true) {
    if (path.basename(dir) !== 'node_modules') dirs.push(path.join(dir, 'node_modules'));
    const parent = path.dirname(dir);
    if (parent === dir) return dirs;
    dir = parent;
  }
}

function isRelative(request) {
  return (
    request === '.' ||
    request === '..' ||
    request.startsWith('./') ||
    request.startsWith('../') ||
    (path.sep === '\\' && (request.startsWith('.\\') || request.startsWith('..\\')))
  );
}

function hasTrailingSlash(request) {
  return (
    request.endsWith('/') ||
    request.endsWith('/.') ||
    request.endsWith('/..') ||
    request === '.' ||
    request === '..' ||
    (path.sep === '\\' && request.endsWith('\\'))
  );
}
