const resolve = require('resolve');

function resolveModule(specifier, basedir) {
  return resolve.sync(specifier, { basedir: basedir || process.cwd() });
}

module.exports = { resolveModule };

if (require.main === module) {
  const [, , specifier, basedir] = process.argv;
  if (!specifier) {
    console.error('Usage: node index.js <module-specifier> [basedir]');
    process.exit(1);
  }
  console.log(resolveModule(specifier, basedir));
}
