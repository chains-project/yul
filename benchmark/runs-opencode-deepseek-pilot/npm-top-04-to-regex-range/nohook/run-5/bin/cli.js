#!/usr/bin/env node
'use strict';

const toRegexRange = require('../index.js');

const input = process.argv[2];

if (!input) {
  console.error('Usage: range-regex <min>-<max>');
  process.exit(1);
}

const match = /^(-?\d+)\s*-\s*(-?\d+)$/.exec(input);

if (!match) {
  console.error(`Invalid range: "${input}". Expected a value like "1-100".`);
  process.exit(1);
}

const min = Number(match[1]);
const max = Number(match[2]);
console.log(toRegexRange(min, max));
