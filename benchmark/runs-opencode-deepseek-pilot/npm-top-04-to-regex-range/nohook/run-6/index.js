#!/usr/bin/env node
'use strict';

const toRegexRange = require('to-regex-range');

const RANGE_RE = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/;

function rangeToRegex(range, options) {
  const match = RANGE_RE.exec(String(range));
  if (!match) {
    throw new TypeError(`Invalid range: "${range}". Expected a string like "1-100".`);
  }

  const source = toRegexRange(match[1], match[2], options);
  return new RegExp(`^${source}$`);
}

module.exports = rangeToRegex;

if (require.main === module) {
  const range = process.argv[2] || '1-100';

  try {
    const regex = rangeToRegex(range);
    console.log(regex.source);
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}
