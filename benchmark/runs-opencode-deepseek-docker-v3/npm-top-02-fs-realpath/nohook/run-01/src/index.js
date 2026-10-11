'use strict';

const fs = require('fs');
const path = require('path');

/**
 * Resolve `target` down to its real, canonical filesystem path, following
 * every symlink (including intermediate directories).
 *
 * The portable JavaScript implementation (`fs.realpathSync`) is used on
 * purpose instead of `fs.realpathSync.native`:
 *
 *   - `fs.realpathSync.native` only exists on some platforms/Node versions.
 *   - The native call delegates to the OS, so it can return a differently
 *     cased path on macOS or an 8.3 short name on Windows.
 *
 * The JS implementation is available on every Node release and yields
 * identical results everywhere, which is what "consistent across Node
 * versions" requires.
 *
 * @param {string} target Path to resolve (absolute or relative to cwd).
 * @param {{ encoding?: BufferEncoding }} [options]
 * @returns {string} The canonical absolute path.
 */
function canonicalPathSync(target, options) {
  if (typeof target !== 'string' || target.length === 0) {
    throw new TypeError('canonicalPathSync expects a non-empty string path');
  }

  const encoding = (options && options.encoding) || 'utf8';
  return fs.realpathSync(path.resolve(target), { encoding });
}

/**
 * Promise-returning variant of {@link canonicalPathSync}. Prefers
 * `fs.promises.realpath` when available and falls back to a callback-based
 * call so the helper also works on older Node releases.
 *
 * @param {string} target
 * @param {{ encoding?: BufferEncoding }} [options]
 * @returns {Promise<string>}
 */
function canonicalPath(target, options) {
  if (typeof target !== 'string' || target.length === 0) {
    return Promise.reject(
      new TypeError('canonicalPath expects a non-empty string path')
    );
  }

  const encoding = (options && options.encoding) || 'utf8';
  const resolved = path.resolve(target);

  if (fs.promises && typeof fs.promises.realpath === 'function') {
    return fs.promises.realpath(resolved, { encoding });
  }

  return new Promise((resolve, reject) => {
    fs.realpath(resolved, { encoding }, (err, real) => {
      if (err) reject(err);
      else resolve(real);
    });
  });
}

module.exports = { canonicalPathSync, canonicalPath };
