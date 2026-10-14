#!/usr/bin/env node
'use strict';

const { rangeToPattern } = require('./range-to-regex');

const args = process.argv.slice(2);
const anchored = !args.includes('--no-anchors');
const range = args.find((a) => !a.startsWith('--'));

if (!range || args.includes('--help')) {
  console.error('Usage: range-to-regex <min>-<max> [--no-anchors]');
  console.error('Example: range-to-regex 1-100');
  process.exit(range ? 0 : 1);
}

try {
  const pattern = rangeToPattern(range);
  console.log(anchored ? `^(?:${pattern})$` : pattern);
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
