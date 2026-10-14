import fs from 'node:fs';
import path from 'node:path';

// Both variants use libuv's uv_fs_realpath (the OS realpath(3) /
// GetFinalPathNameByHandle). The default fs.realpathSync is a JS
// reimplementation whose results differ across platforms and Node versions
// (drive-letter casing, subst/network drives, long paths), so we avoid it.

/**
 * Resolve `p` to its canonical absolute path, following all symlinks.
 * Relative paths are resolved against `cwd`. Rejects if the path does not exist.
 */
export async function resolveRealPath(p, { cwd = process.cwd() } = {}) {
  return fs.promises.realpath(path.resolve(cwd, p));
}

/** Synchronous counterpart of resolveRealPath. */
export function resolveRealPathSync(p, { cwd = process.cwd() } = {}) {
  return fs.realpathSync.native(path.resolve(cwd, p));
}
