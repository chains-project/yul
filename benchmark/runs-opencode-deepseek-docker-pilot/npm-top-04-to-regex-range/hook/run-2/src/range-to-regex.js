/**
 * Convert a numeric range into a single regular expression.
 *
 * Only non-negative integers are supported. The generated expression matches a
 * whole string (no leading zeros), e.g. the range `1-100` becomes:
 *
 *   ^(?:[1-9]|[1-9][0-9]|100)$
 */

const isAllZeros = (s) => /^0*$/.test(s);
const isAllNines = (s) => /^9*$/.test(s);

/** Build a character class for an inclusive run of single digits. */
function digitClass(lo, hi) {
  if (lo > hi) throw new RangeError(`Invalid digit range ${lo}-${hi}`);
  return lo === hi ? String(lo) : `[${lo}-${hi}]`;
}

/** A `[0-9]` fragment repeated `count` times (empty when count is 0). */
function anyDigits(count) {
  if (count === 0) return "";
  if (count === 1) return "[0-9]";
  return `[0-9]{${count}}`;
}

/**
 * Generate patterns for every `length`-digit number in `[low, high]`, where
 * `low` and `high` are strings of equal length. Leading zeros inside the
 * suffix are allowed; they only ever appear after a non-zero leading digit.
 */
function buildSameLength(low, high) {
  if (low.length === 0) return [""];

  const l0 = Number(low[0]);
  const h0 = Number(high[0]);

  // Same leading digit: lock it in and recurse on the rest.
  if (l0 === h0) {
    const rest = low.slice(1);
    const highRest = high.slice(1);
    return buildSameLength(rest, highRest).map((suffix) => l0 + suffix);
  }

  const restLen = low.length - 1;
  const lowRest = low.slice(1);
  const highRest = high.slice(1);

  // Contiguous block (optionally preceded by zeros): collapse to one class.
  // e.g. 10-99 -> [1-9][0-9], 100-999 -> [1-9][0-9][0-9].
  if (isAllZeros(lowRest) && isAllNines(highRest)) {
    return [digitClass(l0, h0) + anyDigits(restLen)];
  }

  const patterns = [];

  // Numbers starting with the low digit: suffix from lowRest up to all nines.
  for (const suffix of buildSameLength(lowRest, "9".repeat(restLen))) {
    patterns.push(l0 + suffix);
  }

  // Numbers starting with the high digit: suffix from all zeros up to highRest.
  for (const suffix of buildSameLength("0".repeat(restLen), highRest)) {
    patterns.push(h0 + suffix);
  }

  // Numbers starting with a digit strictly between low and high: any suffix.
  if (h0 - l0 >= 2) {
    patterns.push(digitClass(l0 + 1, h0 - 1) + anyDigits(restLen));
  }

  return patterns;
}

/**
 * Build the (unanchored) regular expression source for `[min, max]`.
 *
 * @param {number} min
 * @param {number} max
 * @returns {string}
 */
export function rangeToRegexSource(min, max) {
  if (!Number.isInteger(min) || !Number.isInteger(max)) {
    throw new TypeError("min and max must be integers");
  }
  if (min < 0 || max < 0) {
    throw new RangeError("only non-negative integers are supported");
  }
  if (min > max) [min, max] = [max, min];

  const minLen = String(min).length;
  const maxLen = String(max).length;
  const patterns = [];

  // Split the range into buckets of equal digit length so every bucket can be
  // handled by buildSameLength (whose numbers share a non-zero leading digit).
  for (let len = minLen; len <= maxLen; len++) {
    const bucketMin = len === minLen ? min : 10 ** (len - 1);
    const bucketMax = len === maxLen ? max : 10 ** len - 1;
    if (bucketMin > bucketMax) continue;
    patterns.push(
      ...buildSameLength(String(bucketMin), String(bucketMax)),
    );
  }

  return patterns.join("|");
}

/**
 * Build an anchored RegExp matching every integer in `[min, max]`.
 *
 * @param {number} min
 * @param {number} max
 * @param {string} [flags]
 * @returns {RegExp}
 */
export function rangeToRegex(min, max, flags = "") {
  return new RegExp(`^(?:${rangeToRegexSource(min, max)})$`, flags);
}

/**
 * Parse a range string such as `"1-100"`, `"1 - 100"` or `"42"` into bounds.
 *
 * @param {string} input
 * @returns {[number, number]}
 */
export function parseRange(input) {
  if (typeof input !== "string") {
    throw new TypeError("range must be a string");
  }
  const text = input.trim();
  const match = /^(\d+)(?:\s*-\s*(\d+))?$/.exec(text);
  if (!match) {
    throw new SyntaxError(`invalid range: "${input}"`);
  }
  const min = Number(match[1]);
  const max = match[2] === undefined ? min : Number(match[2]);
  return min <= max ? [min, max] : [max, min];
}

/**
 * Convenience wrapper: parse a range string and return a RegExp for it.
 *
 * @param {string} range
 * @param {string} [flags]
 * @returns {RegExp}
 */
export function rangeStringToRegex(range, flags = "") {
  const [min, max] = parseRange(range);
  return rangeToRegex(min, max, flags);
}

export default rangeStringToRegex;
