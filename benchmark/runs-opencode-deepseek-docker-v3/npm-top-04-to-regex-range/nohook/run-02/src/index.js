import toRegexRange from 'to-regex-range';

const DOT_RANGE_PATTERN = /^\s*(-?\d+)\s*\.\.\s*(-?\d+)\s*$/;
const DASH_RANGE_PATTERN = /^\s*(-?\d+)\s*-\s*(\d+)\s*$/;

export function parseRange(input) {
  if (typeof input !== 'string') {
    throw new TypeError('parseRange expects a string such as "1-100"');
  }

  const match = DOT_RANGE_PATTERN.exec(input) || DASH_RANGE_PATTERN.exec(input);
  if (!match) {
    throw new SyntaxError(
      `Invalid range: "${input}" (expected e.g. "1-100", or ".." for negative bounds)`,
    );
  }

  return { min: Number(match[1]), max: Number(match[2]) };
}

export function rangeToRegex(input, options) {
  const { min, max } = typeof input === 'string' ? parseRange(input) : input;

  if (typeof min !== 'number' || typeof max !== 'number') {
    throw new TypeError('rangeToRegex expects a range string or { min, max }');
  }

  if (min > max) {
    throw new RangeError(`Invalid range: min (${min}) must be <= max (${max})`);
  }

  return toRegexRange(min, max, options);
}

export function rangeToRegExp(input, options) {
  return new RegExp(`^(?:${rangeToRegex(input, options)})$`);
}

export default rangeToRegex;
