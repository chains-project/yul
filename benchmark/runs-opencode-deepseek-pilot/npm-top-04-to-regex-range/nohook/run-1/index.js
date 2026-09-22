#!/usr/bin/env node
'use strict';

const toRegexRange = require('to-regex-range');

const RANGE_RE = /^(-?\d+)\s*-\s*(-?\d+)$/;

function parseRange(input) {
  if (Array.isArray(input)) {
    return input.map(Number);
  }

  const match = String(input).trim().match(RANGE_RE);
  if (!match) {
    throw new Error(`Invalid numeric range: ${JSON.stringify(input)}`);
  }

  return [Number(match[1]), Number(match[2])];
}

function rangeToRegex(input) {
  const [min, max] = parseRange(input);

  if (min > max) {
    throw new Error(`Invalid numeric range: ${min} is greater than ${max}`);
  }

  return toRegexRange(min, max);
}

module.exports = rangeToRegex;
module.exports.rangeToRegex = rangeToRegex;
module.exports.parseRange = parseRange;

if (require.main === module) {
  const input = process.argv[2];

  if (!input) {
    console.error('Usage: node index.js <min>-<max>');
    process.exit(1);
  }

  try {
    console.log(rangeToRegex(input));
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}
