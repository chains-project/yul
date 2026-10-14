#!/usr/bin/env node
'use strict';

const { rangeToRegexSource } = require('./range-to-regex');

const args = process.argv.slice(2);
const unanchored = args.includes('--unanchored');
const range = args.find((arg) => !arg.startsWith('--') || /^-\d/.test(arg));

if (!range || args.includes('--help') || args.includes('-h')) {
  console.error('Usage: range-to-regex <min>-<max> [--unanchored]');
  console.error('Example: range-to-regex 1-100');
  process.exit(range ? 0 : 1);
}

try {
  console.log(rangeToRegexSource(range, { anchored: !unanchored }));
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
