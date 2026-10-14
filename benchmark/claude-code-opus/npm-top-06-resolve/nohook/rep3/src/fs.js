import nodeFs from 'node:fs';
import path from 'node:path';
import { invalidPackageConfig } from './errors.js';

// Same encoding as Node's internalModuleStat().
export const MISSING = -1;
export const FILE = 0;
export const DIR = 1;

/**
 * Wraps a node:fs-compatible object (only statSync, readFileSync and
 * realpathSync are used, so memfs and similar virtual filesystems work)
 * with per-instance caches. Call clear() when the filesystem changes,
 * e.g. between rebuilds in watch mode.
 */
export function createCachedFs(fs = nodeFs) {
  const statCache = new Map();
  const realpathCache = new Map();
  const packageCache = new Map();

  function stat(p) {
    let rc = statCache.get(p);
    if (rc === undefined) {
      try {
        const s = fs.statSync(p, { throwIfNoEntry: false });
        rc = !s ? MISSING : s.isDirectory() ? DIR : FILE;
      } catch {
        rc = MISSING;
      }
      statCache.set(p, rc);
    }
    return rc;
  }

  function realpath(p) {
    let real = realpathCache.get(p);
    if (real === undefined) {
      real = fs.realpathSync(p);
      realpathCache.set(p, real);
    }
    return real;
  }

  /**
   * Parsed package.json in `dir`, or null if there is none.
   * Throws ERR_INVALID_PACKAGE_CONFIG on malformed JSON, like Node.
   */
  function readPackage(dir) {
    const pjsonPath = path.join(dir, 'package.json');
    let entry = packageCache.get(pjsonPath);
    if (entry === undefined) {
      let source = null;
      if (stat(pjsonPath) === FILE) {
        try {
          source = fs.readFileSync(pjsonPath, 'utf8');
        } catch {
          source = null;
        }
      }
      if (source === null) {
        entry = null;
      } else {
        try {
          const data = JSON.parse(source);
          entry = { path: pjsonPath, dir, data: data !== null && typeof data === 'object' ? data : {} };
        } catch (err) {
          entry = { error: invalidPackageConfig(pjsonPath, null, err.message) };
        }
      }
      packageCache.set(pjsonPath, entry);
    }
    if (entry?.error) throw entry.error;
    return entry;
  }

  /**
   * Nearest enclosing package.json, walking up from `dir`. Like Node, the
   * walk stops at a node_modules directory rather than escaping it.
   */
  function packageScope(dir) {
    for (let current = path.resolve(dir); ; ) {
      if (path.basename(current) === 'node_modules') return null;
      const pkg = readPackage(current);
      if (pkg) return pkg;
      const parent = path.dirname(current);
      if (parent === current) return null;
      current = parent;
    }
  }

  function clear() {
    statCache.clear();
    realpathCache.clear();
    packageCache.clear();
  }

  return { stat, realpath, readPackage, packageScope, clear };
}
