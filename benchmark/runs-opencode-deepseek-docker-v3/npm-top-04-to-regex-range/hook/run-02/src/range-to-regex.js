import toRegexRange from 'to-regex-range';

/**
 * Parse a range expression into numeric bounds.
 *
 * Accepts "1-100", "1 - 100" or a single value like "42".
 * Ranges must be ordered low-to-high.
 *
 * @param {string|number} input
 * @returns {{min: number, max: number}}
 */
export function parseRange(input) {
  if (typeof input === 'number') {
    if (!Number.isInteger(input)) {
      throw new TypeError(`Expected an integer, got ${input}`);
    }
    return { min: input, max: input };
  }

  if (typeof input !== 'string') {
    throw new TypeError(`Expected a string or number, got ${typeof input}`);
  }

  const trimmed = input.trim();
  const match = /^(-?\d+)(?:\s*-\s*(-?\d+))?$/.exec(trimmed);

  if (!match) {
    throw new SyntaxError(
      `Invalid range "${input}". Expected "min-max" or a single integer.`
    );
  }

  const min = Number(match[1]);
  const max = match[2] === undefined ? min : Number(match[2]);

  if (min > max) {
    throw new RangeError(`Range start ${min} is greater than end ${max}.`);
  }

  return { min, max };
}

/**
 * Build a regular expression that matches any integer in the given range.
 *
 * @param {string|number} input Range such as "1-100" (or a single value).
 * @param {{capture?: boolean, relaxZeros?: boolean, strictZeros?: boolean}} [options]
 * @returns {RegExp}
 */
export function rangeToRegex(input, options = {}) {
  const { capture = false, ...libOptions } = options;
  const { min, max } = parseRange(input);
  const source = toRegexRange(min, max, { ...libOptions, capture: false, wrap: false });
  const group = capture ? `(${source})` : `(?:${source})`;
  return new RegExp(`^${group}$`);
}

export default rangeToRegex;
