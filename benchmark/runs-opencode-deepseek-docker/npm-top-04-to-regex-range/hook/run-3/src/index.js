function assertSafeInteger(value, name) {
  if (typeof value !== "number" || !Number.isSafeInteger(value)) {
    throw new TypeError(`${name} must be a safe integer, received ${value}`);
  }
}

function digitClass(lo, hi) {
  return lo === hi ? String(lo) : `[${lo}-${hi}]`;
}

function digitRun(count) {
  if (count === 0) return "";
  if (count === 1) return "\\d";
  return `\\d{${count}}`;
}

function buildSameLength(lo, hi) {
  if (lo === hi) return lo;

  const length = lo.length;
  const zeros = "0".repeat(length);
  const nines = "9".repeat(length);
  if (lo === zeros && hi === nines) return digitRun(length);

  let index = 0;
  while (lo[index] === hi[index]) index += 1;

  const prefix = lo.slice(0, index);
  const remaining = length - index - 1;
  const loDigit = Number(lo[index]);
  const hiDigit = Number(hi[index]);
  const loRest = lo.slice(index + 1);
  const hiRest = hi.slice(index + 1);
  const restZeros = "0".repeat(remaining);
  const restNines = "9".repeat(remaining);

  const branches = [
    String(loDigit) + buildSameLength(loRest, restNines),
  ];

  if (hiDigit - loDigit >= 2) {
    branches.push(digitClass(loDigit + 1, hiDigit - 1) + digitRun(remaining));
  }

  branches.push(String(hiDigit) + buildSameLength(restZeros, hiRest));

  return `${prefix}(?:${branches.join("|")})`;
}

function splitByLength(min, max) {
  const chunks = [];
  const minLength = String(min).length;
  const maxLength = String(max).length;

  for (let length = minLength; length <= maxLength; length += 1) {
    const lower = length === 1 ? 0 : 10 ** (length - 1);
    const upper = length === maxLength ? max : 10 ** length - 1;
    const start = Math.max(min, lower);
    const end = Math.min(max, upper);
    if (start <= end) chunks.push([start, end]);
  }

  return chunks;
}

/**
 * Build the regular expression source (without anchors) that matches any
 * non-negative integer between `min` and `max` inclusive.
 *
 * @param {number} min
 * @param {number} max
 * @returns {string}
 */
export function rangeToRegexSource(min, max) {
  assertSafeInteger(min, "min");
  assertSafeInteger(max, "max");

  if (min < 0 || max < 0) {
    throw new RangeError("only non-negative integers are supported");
  }
  if (min > max) {
    throw new RangeError(`min (${min}) must be less than or equal to max (${max})`);
  }

  const branches = splitByLength(min, max).map(([lo, hi]) =>
    buildSameLength(String(lo), String(hi))
  );

  return branches.length === 1 ? branches[0] : `(?:${branches.join("|")})`;
}

/**
 * Build an anchored RegExp that matches any number in `[min, max]`.
 *
 * @param {number} min
 * @param {number} max
 * @returns {RegExp}
 */
export function rangeToRegex(min, max) {
  return new RegExp(`^(?:${rangeToRegexSource(min, max)})$`);
}

/**
 * Parse a range expression such as "1-100" into a `[min, max]` tuple.
 *
 * @param {string} input
 * @returns {[number, number]}
 */
export function parseRange(input) {
  const match = /^\s*(\d+)\s*-\s*(\d+)\s*$/.exec(String(input));
  if (!match) {
    throw new SyntaxError(`invalid range "${input}", expected the form "min-max"`);
  }

  const min = Number(match[1]);
  const max = Number(match[2]);
  assertSafeInteger(min, "min");
  assertSafeInteger(max, "max");
  return [min, max];
}
