#!/usr/bin/env node
'use strict';

const toRegexRange = require('to-regex-range');

function rangeToRegex(range) {
  const match = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/.exec(String(range));
  if (!match) {
    throw new TypeError('Expected a numeric range like "1-100"');
  }

  const min = match[1];
  const max = match[2];
  return new RegExp(`^(${toRegexRange(min, max)})$`);
}

module.exports = rangeToRegex;

if (require.main === module) {
  const input = process.argv[2] || '1-100';
  const regex = rangeToRegex(input);
  console.log(regex);
}
