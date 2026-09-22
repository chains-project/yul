'use strict';

const toRegexRange = require('to-regex-range');

const RANGE_RE = /^(-?\d+)-(-?\d+)$/;

function parseRange(range) {
  if (typeof range !== 'string') {
    throw new TypeError('Expected range to be a string, e.g. "1-100"');
  }

  const match = RANGE_RE.exec(range.trim());
  if (!match) {
    throw new TypeError(`Invalid numeric range: ${JSON.stringify(range)}`);
  }

  return { min: Number(match[1]), max: Number(match[2]) };
}

function rangeToRegex(range, options) {
  const { min, max } = parseRange(range);
  return toRegexRange(min, max, options);
}

function rangeToRegExp(range, options) {
  const { min, max } = parseRange(range);
  return new RegExp(`^(?:${toRegexRange(min, max, options)})$`);
}

module.exports = rangeToRegex;
module.exports.rangeToRegex = rangeToRegex;
module.exports.rangeToRegExp = rangeToRegExp;
module.exports.parseRange = parseRange;
