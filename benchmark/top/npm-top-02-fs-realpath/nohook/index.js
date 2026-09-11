const realpath = require('fs.realpath');

const target = process.argv[2];

if (!target) {
  console.error('Usage: node index.js <path>');
  process.exit(1);
}

realpath.realpath(target, (err, resolvedPath) => {
  if (err) {
    console.error(`Failed to resolve real path for "${target}": ${err.message}`);
    process.exit(1);
  }
  console.log(resolvedPath);
});
