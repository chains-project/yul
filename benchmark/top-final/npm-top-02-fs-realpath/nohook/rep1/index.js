const { realpath, realpathSync } = require('fs.realpath');

function resolveRealPath(targetPath, callback) {
  if (typeof callback === 'function') {
    realpath(targetPath, callback);
    return undefined;
  }
  return realpathSync(targetPath);
}

if (require.main === module) {
  const targetPath = process.argv[2];
  if (!targetPath) {
    console.error('Usage: node index.js <path>');
    process.exit(1);
  }

  resolveRealPath(targetPath, (err, resolved) => {
    if (err) {
      console.error(err.message);
      process.exit(1);
    }
    console.log(resolved);
  });
}

module.exports = { resolveRealPath };
