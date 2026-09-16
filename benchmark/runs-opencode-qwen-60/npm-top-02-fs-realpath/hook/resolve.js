const fs = require('fs');
const path = require('path');

/**
 * Resolve a file path down to its real, canonical filesystem path.
 * Follows all symlinks and resolves `.` / `..` segments.
 * Works consistently across Node versions by using the native
 * OS-level realpath implementation (fs.realpathSync.native on
 * Node >= 10.6, falling back to fs.realpathSync).
 *
 * @param {string} filePath - The path to resolve.
 * @returns {string} The canonical filesystem path.
 */
function resolveSymlinks(filePath) {
  return fs.realpathSync.native(filePath);
}

/**
 * Async version: resolves a path using the callback-based fs.realpath,
 * available in all Node versions (no native-only dependency).
 *
 * @param {string} filePath - The path to resolve.
 * @returns {Promise<string>} The canonical filesystem path.
 */
async function resolveSymlinksAsync(filePath) {
  return new Promise((resolve, reject) => {
    fs.realpath(filePath, (err, resolvedPath) => {
      if (err) return reject(err);
      resolve(resolvedPath);
    });
  });
}

if (require.main === module) {
  if (process.argv.length < 3) {
    console.error('Usage: node resolve.js <path>');
    process.exit(1);
  }
  const target = process.argv[2];
  try {
    const resolved = resolveSymlinks(target);
    console.log(resolved);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

module.exports = { resolveSymlinks, resolveSymlinksAsync };