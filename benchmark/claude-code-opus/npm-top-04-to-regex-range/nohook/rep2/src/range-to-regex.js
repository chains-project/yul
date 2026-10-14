'use strict';

const toRegexRange = require('to-regex-range');

/**
 * Parse a range string like "1-100" into [min, max].
 * Accepts surrounding whitespace and negative numbers (e.g. "-10--1").
 */
function parseRange(input) {
  const match = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/.exec(String(input));
  if (!match) {
    throw new Error(`Invalid range "${input}". Expected format: <min>-<max>, e.g. 1-100`);
  }
  let min = Number(match[1]);
  let max = Number(match[2]);
  if (!Number.isSafeInteger(min) || !Number.isSafeInteger(max)) {
    throw new Error(`Range bounds must be safe integers: "${input}"`);
  }
  if (min > max) [min, max] = [max, min];
  return [min, max];
}

/**
 * Convert a range string into a regex source string (no anchors).
 */
function rangeToPattern(input) {
  const [min, max] = parseRange(input);
  return toRegexRange(min, max);
}

/**
 * Convert a range string into an anchored RegExp that matches a whole number in range.
 */
function rangeToRegex(input) {
  return new RegExp(`^(?:${rangeToPattern(input)})$`);
}

module.exports = { parseRange, rangeToPattern, rangeToRegex };
