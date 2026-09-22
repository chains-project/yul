#!/usr/bin/env node
'use strict';

const { rangeToRegex } = require('./index');

const input = process.argv[2];

if (!input) {
  console.error('Usage: range-to-regex <min>-<max>');
  console.error('Example: range-to-regex 1-100');
  process.exit(1);
}

try {
  console.log(rangeToRegex(input));
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
