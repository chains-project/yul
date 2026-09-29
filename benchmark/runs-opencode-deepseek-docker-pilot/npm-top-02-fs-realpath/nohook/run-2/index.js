'use strict';

const fs = require('fs');

function toRealPath(inputPath) {
  return fs.realpathSync(inputPath);
}

function main() {
  const target = process.argv[2];
  if (!target) {
    console.error('Usage: node index.js <path>');
    process.exitCode = 1;
    return;
  }
  process.stdout.write(toRealPath(target) + '\n');
}

if (require.main === module) {
  main();
}

module.exports = { toRealPath };
