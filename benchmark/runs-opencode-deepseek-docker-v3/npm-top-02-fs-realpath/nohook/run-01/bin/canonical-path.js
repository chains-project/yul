#!/usr/bin/env node
'use strict';

const { canonicalPathSync } = require('../src');

function main(argv) {
  const target = argv[0];

  if (!target || target === '-h' || target === '--help') {
    process.stderr.write(
      'Usage: canonical-path <path>\n\n' +
        'Prints the real, canonical filesystem path for <path>.\n'
    );
    return target ? 0 : 2;
  }

  try {
    process.stdout.write(canonicalPathSync(target) + '\n');
    return 0;
  } catch (err) {
    process.stderr.write(`canonical-path: ${err.message}\n`);
    return 1;
  }
}

process.exitCode = main(process.argv.slice(2));
