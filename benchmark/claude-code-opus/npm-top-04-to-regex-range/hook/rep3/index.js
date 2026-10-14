'use strict';

const toRegexRange = require('to-regex-range');

const RANGE_PATTERN = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/;

/**
 * Parse a range string like '1-100' (or '-10--5') into [min, max].
 */
function parseRange(input) {
  const match = RANGE_PATTERN.exec(String(input));
  if (!match) {
    throw new Error(`Invalid range "${input}". Expected format: "<min>-<max>", e.g. "1-100".`);
  }
  const min = Number(match[1]);
  const max = Number(match[2]);
  if (!Number.isSafeInteger(min) || !Number.isSafeInteger(max)) {
    throw new Error(`Range bounds must be safe integers: "${input}".`);
  }
  return min <= max ? [min, max] : [max, min];
}

/**
 * Convert a range string into a regex source string, anchored so it matches
 * the whole input (e.g. '1-100' -> '^(?:[1-9]|[1-9][0-9]|100)$').
 */
function rangeToRegexSource(input, { anchored = true } = {}) {
  const [min, max] = parseRange(input);
  const source = toRegexRange(min, max, { capture: false, shorthand: false });
  // to-regex-range already groups alternations, so anchors can be added directly.
  return anchored ? `^${source}$` : source;
}

/**
 * Convert a range string into a RegExp object.
 */
function rangeToRegex(input, options) {
  return new RegExp(rangeToRegexSource(input, options));
}

module.exports = { parseRange, rangeToRegexSource, rangeToRegex };
