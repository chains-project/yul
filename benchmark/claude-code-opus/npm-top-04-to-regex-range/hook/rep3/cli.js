#!/usr/bin/env node
'use strict';

const { rangeToRegexSource } = require('./index');

const args = process.argv.slice(2);
const unanchored = args.includes('--unanchored');
const ranges = args.filter((a) => a !== '--unanchored');

if (ranges.length === 0) {
  console.error('Usage: range-to-regex [--unanchored] <min-max> [...]');
  console.error('Example: range-to-regex 1-100');
  process.exit(1);
}

try {
  for (const range of ranges) {
    console.log(rangeToRegexSource(range, { anchored: !unanchored }));
  }
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
