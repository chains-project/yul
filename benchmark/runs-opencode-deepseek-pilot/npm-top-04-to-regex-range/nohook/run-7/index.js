'use strict';

const toRegexRange = require('to-regex-range');

const RANGE_RE = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/;

function parseRange(range) {
  const match = RANGE_RE.exec(String(range));
  if (!match) {
    throw new TypeError(`Expected a range like "1-100", got: ${range}`);
  }
  return { min: match[1], max: match[2] };
}

function rangeToRegex(range, options = {}) {
  const { min, max } = parseRange(range);
  const source = toRegexRange(min, max, { capture: true, ...options });
  return new RegExp(`^${source}$`);
}

function rangeToSource(range, options = {}) {
  const { min, max } = parseRange(range);
  return toRegexRange(min, max, options);
}

module.exports = rangeToRegex;
module.exports.rangeToRegex = rangeToRegex;
module.exports.rangeToSource = rangeToSource;
module.exports.parseRange = parseRange;

if (require.main === module) {
  const input = process.argv[2] || '1-100';
  const source = rangeToSource(input, { capture: true });
  console.log(source);
  console.log(rangeToRegex(input));
}
