import toRegexRange from 'to-regex-range';

const RANGE_PATTERN = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/;

/**
 * Parse a range string like "1-100" (or "-10--5") into [min, max].
 */
export function parseRange(input) {
  const match = RANGE_PATTERN.exec(input);
  if (!match) {
    throw new Error(`Invalid range "${input}". Expected format: <min>-<max>, e.g. 1-100`);
  }
  const min = Number(match[1]);
  const max = Number(match[2]);
  if (!Number.isSafeInteger(min) || !Number.isSafeInteger(max)) {
    throw new Error(`Range bounds must be safe integers: "${input}"`);
  }
  return min <= max ? [min, max] : [max, min];
}

/**
 * Build a RegExp that matches exactly the integers in the given range.
 * Anchored by default so "150" doesn't match inside 1-100 via "15".
 */
export function rangeToRegex(input, { anchored = true } = {}) {
  const [min, max] = parseRange(input);
  const source = toRegexRange(min, max, { capture: false, shorthand: true });
  return new RegExp(anchored ? `^(?:${source})$` : source);
}
