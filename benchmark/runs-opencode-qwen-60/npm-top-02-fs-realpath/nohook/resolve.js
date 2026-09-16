const fs = require('fs');
const path = require('path');

const target = process.argv[2];

if (!target) {
  console.error('Usage: node resolve.js <path>');
  process.exit(1);
}

try {
  const resolved = fs.realpathSync.native(target);
  console.log(resolved);
} catch (err) {
  if (err.code === 'ENOENT') {
    process.stderr.write(`ENOENT: no such file or directory, realpath '${target}'\n`);
    process.exit(1);
  }
  throw err;
}