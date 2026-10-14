import fs from 'node:fs';
import path from 'node:path';

// Node ships two realpath implementations:
//   - fs.realpath / fs.realpathSync: a JavaScript reimplementation that walks
//     each path component with lstat/readlink. Its behavior has shifted across
//     releases and differs from the OS on Windows (subst/mapped drives, casing,
//     long paths).
//   - fs.realpath.native / fs.realpathSync.native / fs.promises.realpath: thin
//     wrappers over libuv's uv_fs_realpath, i.e. realpath(3) on POSIX and
//     GetFinalPathNameByHandleW on Windows.
// We always use the native variant so the result is whatever the OS considers
// canonical, independent of the Node version running the script.

/**
 * Resolve `p` (relative paths are resolved against `cwd`) to its canonical
 * path, following every symlink. The target must exist.
 * @param {string} p
 * @param {{ cwd?: string }} [options]
 * @returns {Promise<string>}
 */
export async function resolveRealPath(p, { cwd = process.cwd() } = {}) {
  return fs.promises.realpath(toAbsolute(p, cwd));
}

/**
 * Synchronous variant of {@link resolveRealPath}.
 * @param {string} p
 * @param {{ cwd?: string }} [options]
 * @returns {string}
 */
export function resolveRealPathSync(p, { cwd = process.cwd() } = {}) {
  return fs.realpathSync.native(toAbsolute(p, cwd));
}

function toAbsolute(p, cwd) {
  if (typeof p !== 'string' || p === '') {
    throw new TypeError('path must be a non-empty string');
  }
  return path.resolve(cwd, p);
}
