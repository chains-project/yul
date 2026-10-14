'use strict';

const toRegexRange = require('to-regex-range');

const RANGE_PATTERN = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/;

/**
 * Convert a range string like "1-100" into a regex source string that
 * matches any integer in that range (inclusive).
 *
 * @param {string} range - e.g. "1-100", "-5-10", "-20--10"
 * @param {object} [options]
 * @param {boolean} [options.anchored=true] - wrap the pattern in ^...$
 * @returns {string}
 */
function rangeToRegexSource(range, { anchored = true } = {}) {
  const match = RANGE_PATTERN.exec(String(range));
  if (!match) {
    throw new Error(`Invalid range "${range}". Expected format: <min>-<max>, e.g. 1-100`);
  }

  let [min, max] = [Number(match[1]), Number(match[2])];
  if (!Number.isSafeInteger(min) || !Number.isSafeInteger(max)) {
    throw new Error(`Range bounds must be safe integers: "${range}"`);
  }
  if (min > max) [min, max] = [max, min];

  const source = toRegexRange(min, max, { capture: false, shorthand: true });
  // to-regex-range already groups alternations, so anchoring needs no extra group.
  return anchored ? `^${source}$` : source;
}

/**
 * Same as rangeToRegexSource, but returns a RegExp object.
 */
function rangeToRegex(range, options) {
  return new RegExp(rangeToRegexSource(range, options));
}

module.exports = { rangeToRegex, rangeToRegexSource };
