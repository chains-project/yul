import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Node ships two realpath implementations:
//   - fs.realpath / fs.realpathSync: a JS reimplementation that walks the path
//     with lstat/readlink. Its output has differed between Node versions and
//     platforms (e.g. path casing on case-insensitive filesystems).
//   - fs.realpathSync.native / fs.promises.realpath: thin wrappers over libuv's
//     uv_fs_realpath (realpath(3) on POSIX, GetFinalPathNameByHandleW on
//     Windows), so the result is defined by the OS and stable across Node
//     versions.
// We always use the native implementation, falling back to the JS one only
// when the native call fails for reasons other than "the path can't be
// resolved" (known to happen on some Windows RAM disks, virtual drives and
// network shares).

const UNRESOLVABLE = new Set(['ENOENT', 'ENOTDIR', 'ELOOP', 'EACCES', 'ENAMETOOLONG']);

function shouldFallBack(err) {
  return typeof err?.code === 'string' && !UNRESOLVABLE.has(err.code);
}

function toAbsolute(p) {
  if (p instanceof URL) return fileURLToPath(p);
  if (Buffer.isBuffer(p)) p = p.toString();
  if (typeof p !== 'string' || p.length === 0) {
    throw new TypeError('path must be a non-empty string, Buffer, or file: URL');
  }
  return path.resolve(p);
}

/**
 * Resolve `p` to its canonical absolute path: relative paths are resolved
 * against process.cwd(), and all symlinks, `.` and `..` are resolved.
 * Rejects (e.g. with ENOENT) if any component does not exist.
 *
 * @param {string | Buffer | URL} p
 * @returns {Promise<string>}
 */
export async function canonicalPath(p) {
  const abs = toAbsolute(p);
  try {
    return await fs.promises.realpath(abs);
  } catch (err) {
    if (!shouldFallBack(err)) throw err;
    return fs.realpathSync(abs);
  }
}

/**
 * Synchronous variant of {@link canonicalPath}.
 *
 * @param {string | Buffer | URL} p
 * @returns {string}
 */
export function canonicalPathSync(p) {
  const abs = toAbsolute(p);
  try {
    return fs.realpathSync.native(abs);
  } catch (err) {
    if (!shouldFallBack(err)) throw err;
    return fs.realpathSync(abs);
  }
}
