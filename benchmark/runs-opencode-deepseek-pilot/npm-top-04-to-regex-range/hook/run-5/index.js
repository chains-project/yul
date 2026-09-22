#!/usr/bin/env node
'use strict';

const toRegexRange = require('to-regex-range');

/**
 * Convert a numeric range string like "1-100" into a single RegExp
 * that matches any number within that (inclusive) range.
 *
 * @param {string} range  Range in "<min>-<max>" form, e.g. "1-100".
 * @param {object} [options]  Options forwarded to to-regex-range.
 * @returns {RegExp}
 */
function rangeToRegex(range, options) {
  if (typeof range !== 'string') {
    throw new TypeError('Expected a string range like "1-100"');
  }

  const match = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/.exec(range);
  if (!match) {
    throw new Error(`Invalid range: "${range}" (expected "<min>-<max>")`);
  }

  const [, min, max] = match;
  const source = toRegexRange(min, max, options);
  return new RegExp(`^(?:${source})$`);
}

module.exports = rangeToRegex;

if (require.main === module) {
  const arg = process.argv[2];
  if (!arg) {
    console.error('Usage: range-to-regex <min>-<max>');
    process.exit(1);
  }

  try {
    console.log(rangeToRegex(arg).source);
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}
