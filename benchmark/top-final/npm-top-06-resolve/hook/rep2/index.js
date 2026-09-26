const resolve = require('resolve');

function resolveModule(request, basedir = process.cwd()) {
  return new Promise((res, rej) => {
    resolve(request, { basedir }, (err, resolvedPath) => {
      if (err) return rej(err);
      res(resolvedPath);
    });
  });
}

function resolveModuleSync(request, basedir = process.cwd()) {
  return resolve.sync(request, { basedir });
}

module.exports = { resolveModule, resolveModuleSync };

if (require.main === module) {
  const target = process.argv[2] || 'resolve';
  resolveModule(target)
    .then((resolvedPath) => console.log(`${target} -> ${resolvedPath}`))
    .catch((err) => {
      console.error(err.message);
      process.exitCode = 1;
    });
}
