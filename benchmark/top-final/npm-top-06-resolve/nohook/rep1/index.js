const resolve = require('resolve');

function resolveModule(request, basedir) {
  return resolve.sync(request, { basedir });
}

module.exports = { resolveModule };

if (require.main === module) {
  const [request, basedir = process.cwd()] = process.argv.slice(2);
  if (!request) {
    console.error('Usage: node index.js <module-request> [basedir]');
    process.exit(1);
  }
  console.log(resolveModule(request, basedir));
}
