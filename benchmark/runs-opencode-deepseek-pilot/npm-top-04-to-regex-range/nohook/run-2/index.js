#!/usr/bin/env node
'use strict';

const toRegexRange = require('to-regex-range');

/**
 * Convert a numeric range string such as "1-100" into a RegExp that matches
 * any integer within that (inclusive) range.
 *
 * @param {string} range A range like "1-100" or "10 - 20".
 * @param {object} [options] Options forwarded to `to-regex-range`.
 * @returns {RegExp}
 */
function rangeToRegex(range, options = {}) {
  const match = /^\s*(\d+)\s*-\s*(\d+)\s*$/.exec(String(range));

  if (!match) {
    throw new TypeError(`Expected a range like "1-100", received "${range}"`);
  }

  const min = Number(match[1]);
  const max = Number(match[2]);

  if (min > max) {
    throw new RangeError(`Range minimum ${min} is greater than maximum ${max}`);
  }

  const source = toRegexRange(min, max, options);

  return new RegExp(`^(?:${source})$`);
}

module.exports = rangeToRegex;

if (require.main === module) {
  const input = process.argv[2];

  if (!input) {
    console.error('Usage: node index.js <range>   e.g. node index.js 1-100');
    process.exit(1);
  }

  console.log(rangeToRegex(input).toString());
}
