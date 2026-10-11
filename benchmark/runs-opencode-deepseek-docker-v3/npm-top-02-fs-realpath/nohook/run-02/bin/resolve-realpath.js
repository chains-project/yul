#!/usr/bin/env node
'use strict';

const realpath = require('../index.js');

const USAGE = 'Usage: realpath-resolver <path>';

function main(argv) {
  const target = argv[2];

  if (!target || target === '-h' || target === '--help') {
    process.stderr.write(USAGE + '\n');
    process.exit(target ? 0 : 2);
  }

  return realpath.sync(target);
}

try {
  process.stdout.write(main(process.argv) + '\n');
} catch (err) {
  process.stderr.write('realpath-resolver: ' + err.message + '\n');
  process.exit(1);
}
