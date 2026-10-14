#!/usr/bin/env node
'use strict';

const toRegexRange = require('to-regex-range');

/**
 * Convert a range string like "1-100" into a RegExp that matches
 * exactly the integers in that range (inclusive).
 */
function rangeToRegex(range) {
  const match = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/.exec(String(range));
  if (!match) {
    throw new Error(`Invalid range "${range}". Expected format: "min-max", e.g. "1-100".`);
  }

  let [min, max] = [Number(match[1]), Number(match[2])];
  if (min > max) [min, max] = [max, min];

  const source = toRegexRange(min, max, { capture: false, shorthand: true });
  return new RegExp(`^(?:${source})$`);
}

module.exports = { rangeToRegex };

if (require.main === module) {
  const arg = process.argv[2];
  if (!arg) {
    console.error('Usage: range-to-regex <min-max>   e.g. range-to-regex 1-100');
    process.exit(1);
  }
  try {
    console.log(rangeToRegex(arg).source);
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}
