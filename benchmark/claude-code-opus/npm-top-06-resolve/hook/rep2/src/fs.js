import nodeFs from 'node:fs';
import path from 'node:path';
import { invalidPackageConfig } from './errors.js';

/**
 * The minimal synchronous filesystem surface the resolver needs. Build tools
 * can supply their own implementation (virtual files, in-memory overlays,
 * watch-mode caches, ...).
 *
 * @typedef {object} ResolverFs
 * @property {(p: string) => 'file' | 'dir' | null} stat
 * @property {(p: string) => string | null} readFile  Returns null if missing.
 * @property {(p: string) => string} realpath
 */

/** @type {ResolverFs} */
export const defaultFs = {
  stat(p) {
    const s = nodeFs.statSync(p, { throwIfNoEntry: false });
    if (!s) return null;
    return s.isDirectory() ? 'dir' : 'file';
  },
  readFile(p) {
    try {
      return nodeFs.readFileSync(p, 'utf8');
    } catch (err) {
      if (err.code === 'ENOENT' || err.code === 'ENOTDIR' || err.code === 'EISDIR') return null;
      throw err;
    }
  },
  realpath(p) {
    return nodeFs.realpathSync.native(p);
  },
};

/**
 * @typedef {object} PackageJson
 * @property {string} path      Absolute path to the package.json file.
 * @property {string} dir       Directory containing it.
 * @property {string} [name]
 * @property {string} [main]
 * @property {unknown} [exports]
 * @property {unknown} [imports]
 */

/**
 * Wraps a ResolverFs with memoisation. A single cache instance should live as
 * long as the filesystem is assumed unchanged (e.g. one build); call
 * `clear()` on file changes in watch mode.
 *
 * @param {ResolverFs} fs
 */
export function createCachedFs(fs) {
  /** @type {Map<string, 'file' | 'dir' | null>} */
  const statCache = new Map();
  /** @type {Map<string, PackageJson | null>} */
  const pkgCache = new Map();
  /** @type {Map<string, string>} */
  const realpathCache = new Map();

  /** @param {string} p */
  function stat(p) {
    let v = statCache.get(p);
    if (v === undefined) {
      v = fs.stat(p);
      statCache.set(p, v);
    }
    return v;
  }

  /**
   * Reads and parses `<dir>/package.json`. Returns null if absent.
   * Like Node, only the fields relevant to resolution are kept.
   *
   * @param {string} dir
   * @returns {PackageJson | null}
   */
  function readPackageJson(dir) {
    if (pkgCache.has(dir)) return /** @type {PackageJson | null} */ (pkgCache.get(dir));
    const file = path.join(dir, 'package.json');
    const text = fs.readFile(file);
    /** @type {PackageJson | null} */
    let pkg = null;
    if (text !== null) {
      let json;
      try {
        json = JSON.parse(text);
      } catch (err) {
        throw invalidPackageConfig(file, /** @type {Error} */ (err).message);
      }
      pkg = {
        path: file,
        dir,
        name: typeof json.name === 'string' ? json.name : undefined,
        main: typeof json.main === 'string' ? json.main : undefined,
        exports: json.exports,
        imports: json.imports,
      };
    }
    pkgCache.set(dir, pkg);
    return pkg;
  }

  /**
   * Finds the nearest package.json at or above `dir`, not crossing a
   * `node_modules` boundary (mirrors Node's package scope lookup).
   *
   * @param {string} dir
   * @returns {PackageJson | null}
   */
  function findPackageScope(dir) {
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

  /** @param {string} p */
  function realpath(p) {
    let v = realpathCache.get(p);
    if (v === undefined) {
      v = fs.realpath(p);
      realpathCache.set(p, v);
    }
    return v;
  }

  return {
    stat,
    isFile: (/** @type {string} */ p) => stat(p) === 'file',
    isDir: (/** @type {string} */ p) => stat(p) === 'dir',
    readPackageJson,
    findPackageScope,
    realpath,
    clear() {
      statCache.clear();
      pkgCache.clear();
      realpathCache.clear();
    },
  };
}

/** @typedef {ReturnType<typeof createCachedFs>} CachedFs */
