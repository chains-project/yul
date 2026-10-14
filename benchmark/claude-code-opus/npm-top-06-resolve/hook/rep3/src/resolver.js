/**
 * Node's CommonJS resolution algorithm (`require.resolve`), as described in
 * https://nodejs.org/api/modules.html#all-together and implemented in
 * lib/internal/modules/cjs/loader.js. Where the docs and the implementation
 * disagree, this follows the implementation.
 */

import path from 'node:path';
import { isBuiltin } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { invalidModuleSpecifier, invalidPackageConfig, moduleNotFound } from './errors.js';
import { nodeFsHost } from './fs-host.js';
import { packageExportsResolve, packageImportsResolve } from './package-exports.js';

// Package name (optionally scoped) followed by an optional subpath.
const EXPORTS_PATTERN = /^((?:@[^/\\%]+\/)?[^./\\%][^/\\%]*)(\/.*)?$/;
const ENCODED_SEP_REGEX = /%2F|%5C/i;

export const DEFAULT_EXTENSIONS = Object.freeze(['.js', '.json', '.node']);

/** Conditions Node's CJS loader uses for "exports"/"imports" in this runtime. */
export const DEFAULT_CONDITIONS = Object.freeze([
  'require',
  'node',
  ...(process.features.require_module ? ['module-sync'] : []),
]);

export class Resolver {
  #host;
  #extensions;
  #conditions;
  #preserveSymlinks;
  #paths;
  #packageCache = new Map();

  /** @param {import('./index.js').ResolverOptions} [options] */
  constructor(options = {}) {
    this.#host = options.fs ?? nodeFsHost;
    this.#extensions = [...(options.extensions ?? DEFAULT_EXTENSIONS)];
    this.#conditions = new Set(options.conditions ?? DEFAULT_CONDITIONS);
    this.#preserveSymlinks = options.preserveSymlinks ?? false;
    this.#paths = [...(options.paths ?? [])];
  }

  /** Drops cached package.json contents (call after the filesystem changes). */
  clearCache() {
    this.#packageCache.clear();
  }

  /**
   * Resolves `request` as if `require.resolve(request)` were called from the
   * file `parentPath`. A `parentPath` ending in a path separator is treated as
   * a directory, mirroring `createRequire`.
   *
   * @param {string} request
   * @param {string} parentPath absolute path of the requiring file
   * @returns {string} absolute file path, or the builtin id (e.g. "fs", "node:test")
   */
  resolve(request, parentPath) {
    if (typeof request !== 'string' || request === '') {
      throw new TypeError('request must be a non-empty string');
    }
    if (typeof parentPath !== 'string' || !path.isAbsolute(parentPath)) {
      throw new TypeError('parentPath must be an absolute path');
    }

    if (isBuiltin(request)) return request;

    const parentDir = /[\\/]$/.test(parentPath) ? parentPath : path.dirname(parentPath);
    // Used as the "imported from" location for package scope lookups.
    const parentFile = parentDir === parentPath ? path.join(parentDir, 'noop.js') : parentPath;

    if (request[0] === '#') {
      const scope = this.#readPackageScope(parentFile);
      if (scope?.data.imports != null) {
        return this.#finalizeEsmResolution(request, parentPath, () =>
          packageImportsResolve(request, scope.data.imports, this.#exportsContext(scope.pjsonPath)),
        );
      }
    }

    const selfResolved = this.#trySelf(request, parentFile, parentPath);
    if (selfResolved) return selfResolved;

    const filename = this.#findPath(request, this.#lookupPaths(request, parentDir));
    if (filename) return filename;

    throw moduleNotFound(request, parentPath);
  }

  // LOAD_PACKAGE_SELF
  #trySelf(request, parentFile, parentPath) {
    const scope = this.#readPackageScope(parentFile);
    if (!scope || scope.data.exports == null || typeof scope.data.name !== 'string') return false;

    const { name } = scope.data;
    let subpath;
    if (request === name) subpath = '.';
    else if (request.startsWith(`${name}/`)) subpath = `.${request.slice(name.length)}`;
    else return false;

    return this.#finalizeEsmResolution(request, parentPath, () =>
      packageExportsResolve(subpath, scope.data.exports, this.#exportsContext(scope.pjsonPath)),
    );
  }

  #lookupPaths(request, parentDir) {
    if (isRelative(request)) return [parentDir];
    if (path.isAbsolute(request)) return [''];
    return [...nodeModulesPaths(parentDir), ...this.#paths];
  }

  // Module._findPath: LOAD_AS_FILE / LOAD_AS_DIRECTORY / LOAD_NODE_MODULES
  #findPath(request, paths) {
    const absoluteRequest = path.isAbsolute(request);
    const trailingSlash = hasTrailingSlash(request);

    for (const curPath of paths) {
      if (curPath && this.#host.stat(curPath) !== 'directory') continue;

      if (!absoluteRequest) {
        const exportsResolved = this.#resolveExports(curPath, request);
        if (exportsResolved) return exportsResolved;
      }

      const basePath = path.resolve(curPath, request);
      const kind = this.#host.stat(basePath);
      let filename;

      if (!trailingSlash) {
        if (kind === 'file') filename = this.#toRealPath(basePath);
        filename ||= this.#tryExtensions(basePath);
      }
      if (!filename && kind === 'directory') {
        filename = this.#tryPackage(basePath, request);
      }
      if (filename) return filename;
    }
    return false;
  }

  // LOAD_PACKAGE_EXPORTS
  #resolveExports(nmPath, request) {
    const match = EXPORTS_PATTERN.exec(request);
    if (!match) return undefined;
    const [, name, expansion = ''] = match;

    const pkgDir = path.resolve(nmPath, name);
    const pjsonPath = path.join(pkgDir, 'package.json');
    const pkg = this.#readPackage(pjsonPath);
    if (!pkg || pkg.exports == null) return undefined;

    return this.#finalizeEsmResolution(request, undefined, () =>
      packageExportsResolve(`.${expansion}`, pkg.exports, this.#exportsContext(pjsonPath)),
    );
  }

  // LOAD_AS_DIRECTORY
  #tryPackage(dir, originalRequest) {
    const pjsonPath = path.join(dir, 'package.json');
    const main = this.#readPackage(pjsonPath)?.main;
    if (typeof main !== 'string' || main === '') return this.#tryIndex(dir);

    const mainPath = path.resolve(dir, main);
    const filename =
      this.#tryFile(mainPath) || this.#tryExtensions(mainPath) || this.#tryIndex(mainPath) || this.#tryIndex(dir); // DEP0128

    if (filename) return filename;
    const err = moduleNotFound(originalRequest);
    err.message = `Cannot find module '${mainPath}'. Please verify that the package.json has a valid "main" entry`;
    err.path = pjsonPath;
    err.requestPath = originalRequest;
    throw err;
  }

  // LOAD_INDEX
  #tryIndex(dir) {
    return this.#tryExtensions(path.resolve(dir, 'index'));
  }

  #tryExtensions(basePath) {
    for (const ext of this.#extensions) {
      const filename = this.#tryFile(basePath + ext);
      if (filename) return filename;
    }
    return false;
  }

  #tryFile(p) {
    return this.#host.stat(p) === 'file' ? this.#toRealPath(p) : false;
  }

  #toRealPath(p) {
    return this.#preserveSymlinks ? p : this.#host.realpath(p);
  }

  // RESOLVE_ESM_MATCH
  #finalizeEsmResolution(request, parentPath, resolveURL) {
    let url;
    try {
      url = resolveURL();
    } catch (err) {
      if (err.code === 'ERR_MODULE_NOT_FOUND') throw moduleNotFound(request, parentPath);
      throw err;
    }

    if (url.protocol === 'node:') return url.pathname;
    if (ENCODED_SEP_REGEX.test(url.pathname)) {
      throw invalidModuleSpecifier(url.pathname, 'must not include encoded "/" or "\\" characters');
    }

    const filename = this.#tryFile(fileURLToPath(url));
    if (filename) return filename;
    throw moduleNotFound(request, parentPath);
  }

  /**
   * ESM PACKAGE_RESOLVE, used only for bare-specifier targets of "imports"
   * (e.g. `"#dep": "dep/sub"`), matching what Node's CJS loader delegates to.
   * @returns {URL}
   */
  #esmPackageResolve(specifier, baseURL) {
    if (isBuiltin(specifier)) return new URL(`node:${specifier}`);

    const match = EXPORTS_PATTERN.exec(specifier);
    if (!match) throw invalidModuleSpecifier(specifier, 'is not a valid package name');
    const [, name, expansion = ''] = match;
    const subpath = `.${expansion}`;
    const basePath = fileURLToPath(baseURL);

    const self = this.#readPackageScope(basePath);
    if (self?.data.name === name && self.data.exports != null) {
      return packageExportsResolve(subpath, self.data.exports, this.#exportsContext(self.pjsonPath));
    }

    for (const nmPath of nodeModulesPaths(path.dirname(basePath))) {
      const pkgDir = path.join(nmPath, name);
      if (this.#host.stat(pkgDir) !== 'directory') continue;

      const pjsonPath = path.join(pkgDir, 'package.json');
      const pkg = this.#readPackage(pjsonPath);
      if (pkg?.exports != null) {
        return packageExportsResolve(subpath, pkg.exports, this.#exportsContext(pjsonPath));
      }
      if (subpath === '.') return this.#legacyMainResolve(pkgDir, pkg);
      return pathToFileURL(path.join(pkgDir, expansion));
    }

    const err = moduleNotFound(specifier);
    err.code = 'ERR_MODULE_NOT_FOUND';
    throw err;
  }

  #legacyMainResolve(pkgDir, pkg) {
    const candidates = [];
    if (typeof pkg?.main === 'string') {
      const main = pkg.main;
      candidates.push(main, `${main}.js`, `${main}.json`, `${main}.node`);
      candidates.push(`${main}/index.js`, `${main}/index.json`, `${main}/index.node`);
    }
    candidates.push('index.js', 'index.json', 'index.node');

    for (const candidate of candidates) {
      const p = path.resolve(pkgDir, candidate);
      if (this.#host.stat(p) === 'file') return pathToFileURL(p);
    }
    const err = moduleNotFound(pkgDir);
    err.code = 'ERR_MODULE_NOT_FOUND';
    throw err;
  }

  #exportsContext(pjsonPath) {
    return {
      pjsonURL: pathToFileURL(pjsonPath),
      conditions: this.#conditions,
      packageResolve: (specifier, baseURL) => this.#esmPackageResolve(specifier, baseURL),
    };
  }

  /**
   * Finds the closest package.json above `filePath`, stopping at a
   * node_modules boundary (LOOKUP_PACKAGE_SCOPE).
   * @returns {{ pjsonPath: string, data: any } | undefined}
   */
  #readPackageScope(filePath) {
    let dir = path.dirname(filePath);
    while (true) {
      if (path.basename(dir) === 'node_modules') return undefined;
      const pjsonPath = path.join(dir, 'package.json');
      const data = this.#readPackage(pjsonPath);
      if (data) return { pjsonPath, data };
      const parent = path.dirname(dir);
      if (parent === dir) return undefined;
      dir = parent;
    }
  }

  /** @returns {object | undefined} parsed package.json, or undefined if absent */
  #readPackage(pjsonPath) {
    if (this.#packageCache.has(pjsonPath)) return this.#packageCache.get(pjsonPath);

    const source = this.#host.readFile(pjsonPath);
    let data;
    if (source !== undefined) {
      try {
        data = JSON.parse(source);
      } catch (err) {
        throw invalidPackageConfig(pjsonPath, err.message);
      }
      // Non-object JSON (e.g. `"str"` or `null`) behaves like an empty package.
      if (data === null || typeof data !== 'object') data = {};
    }
    this.#packageCache.set(pjsonPath, data);
    return data;
  }
}

/** NODE_MODULES_PATHS: every ancestor's node_modules, skipping node_modules/node_modules. */
export function nodeModulesPaths(from) {
  from = path.resolve(from);
  const dirs = [];
  let dir = from;
  while (true) {
    if (path.basename(dir) !== 'node_modules') dirs.push(path.join(dir, 'node_modules'));
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return dirs;
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

// "dir/", ".", "..", "dir/." and "dir/.." only ever resolve as directories.
function hasTrailingSlash(request) {
  return /(?:^|[\\/])\.{1,2}$/.test(request) || /[\\/]$/.test(request);
}
