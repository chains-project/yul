import fs from 'node:fs';
import path from 'node:path';

// Node ships two realpath implementations:
//   - fs.realpath / fs.realpathSync: a JavaScript re-implementation that walks
//     each path segment with lstat/readlink. Its behavior has shifted between
//     Node versions and differs from the OS (e.g. Windows drive-letter casing,
//     subst drives, junctions, named pipes).
//   - fs.realpath.native / fs.realpathSync.native / fs.promises.realpath:
//     delegate to libuv's uv_fs_realpath, i.e. the OS realpath(3) /
//     GetFinalPathNameByHandle. This is what the kernel considers canonical.
// We always use the native variant so results match the OS and stay stable
// across Node releases.

/**
 * Resolve `p` (relative to process.cwd() if not absolute) to its canonical
 * path with all symlinks, `.` and `..` segments resolved.
 * Rejects with ENOENT if any component does not exist.
 * @param {string} p
 * @returns {Promise<string>}
 */
export async function resolveRealPath(p) {
  return fs.promises.realpath(path.resolve(p));
}

/**
 * Synchronous variant of {@link resolveRealPath}.
 * @param {string} p
 * @returns {string}
 */
export function resolveRealPathSync(p) {
  return fs.realpathSync.native(path.resolve(p));
}
