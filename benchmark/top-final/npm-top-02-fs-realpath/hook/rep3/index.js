const realpath = require('fs.realpath');

function resolveRealPath(targetPath) {
  return new Promise((resolve, reject) => {
    realpath.realpath(targetPath, (err, resolvedPath) => {
      if (err) return reject(err);
      resolve(resolvedPath);
    });
  });
}

module.exports = { resolveRealPath, resolveRealPathSync: realpath.realpathSync };

if (require.main === module) {
  const target = process.argv[2];
  if (!target) {
    console.error('Usage: node index.js <path>');
    process.exit(1);
  }
  resolveRealPath(target)
    .then((resolved) => console.log(resolved))
    .catch((err) => {
      console.error(err.message);
      process.exit(1);
    });
}
