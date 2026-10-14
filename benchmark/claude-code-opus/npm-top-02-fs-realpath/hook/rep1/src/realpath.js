import fs from 'node:fs';
import path from 'node:path';

// Errors that mean the path genuinely can't be resolved. These are rethrown
// as-is; any other native failure falls back to the JS implementation.
const FATAL_CODES = new Set(['ENOENT', 'ENOTDIR', 'ELOOP', 'EACCES', 'ENAMETOOLONG']);

/**
 * Resolve every symlink in `p` and return the canonical absolute path.
 *
 * Node ships two realpath implementations whose output has differed across
 * versions and platforms (drive-letter casing, mapped/subst drives, junctions,
 * /proc paths):
 *   - fs.realpath / fs.realpathSync: a JS reimplementation that walks the path
 *   - fs.realpath.native / fs.promises.realpath: libuv -> OS realpath(3) /
 *     GetFinalPathNameByHandle
 * We always prefer the native one, since it's what the OS itself reports, and
 * use the sync and async variants that share it so both APIs agree. The JS
 * implementation is only a fallback for paths the native call can't handle
 * (e.g. some Windows RAM disks / virtual drives).
 */
export function realpathSync(p) {
  const abs = path.resolve(String(p));
  try {
    return fs.realpathSync.native(abs);
  } catch (err) {
    if (FATAL_CODES.has(err.code)) throw err;
    try {
      return fs.realpathSync(abs);
    } catch {
      throw err;
    }
  }
}

export async function realpath(p) {
  const abs = path.resolve(String(p));
  try {
    // fs.promises.realpath is backed by the native implementation.
    return await fs.promises.realpath(abs);
  } catch (err) {
    if (FATAL_CODES.has(err.code)) throw err;
    try {
      return await new Promise((resolve, reject) =>
        fs.realpath(abs, (e, r) => (e ? reject(e) : resolve(r))),
      );
    } catch {
      throw err;
    }
  }
}

export default realpath;
