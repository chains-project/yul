const resolve = require('resolve');

/**
 * Resolve a module specifier the same way Node's require.resolve() would,
 * starting the lookup from `basedir`.
 *
 * @param {string} specifier - module specifier, e.g. './foo' or 'lodash'
 * @param {string} basedir - directory to resolve relative to
 * @returns {string} absolute path to the resolved file
 */
function resolveModule(specifier, basedir = process.cwd()) {
  return resolve.sync(specifier, {
    basedir,
    extensions: ['.js', '.json', '.node'],
  });
}

/**
 * Async variant, useful when resolving many specifiers without blocking
 * the event loop (e.g. across a whole dependency graph).
 */
function resolveModuleAsync(specifier, basedir = process.cwd()) {
  return new Promise((resolvePromise, reject) => {
    resolve(
      specifier,
      { basedir, extensions: ['.js', '.json', '.node'] },
      (err, resolvedPath) => {
        if (err) reject(err);
        else resolvePromise(resolvedPath);
      }
    );
  });
}

module.exports = { resolveModule, resolveModuleAsync };

if (require.main === module) {
  const [specifier, basedir] = process.argv.slice(2);
  if (!specifier) {
    console.error('Usage: node index.js <specifier> [basedir]');
    process.exit(1);
  }
  try {
    console.log(resolveModule(specifier, basedir));
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}
