const resolve = require('resolve');
const path = require('path');

function resolveModule(request, basedir) {
  return new Promise((res, rej) => {
    resolve(request, { basedir }, (err, resolved) => {
      if (err) return rej(err);
      res(resolved);
    });
  });
}

async function main() {
  const target = process.argv[2];
  if (!target) {
    console.error('Usage: node index.js <module-specifier>');
    process.exit(1);
  }

  try {
    const resolved = await resolveModule(target, process.cwd());
    console.log(path.relative(process.cwd(), resolved));
  } catch (err) {
    console.error(`Could not resolve "${target}": ${err.message}`);
    process.exit(1);
  }
}

main();
