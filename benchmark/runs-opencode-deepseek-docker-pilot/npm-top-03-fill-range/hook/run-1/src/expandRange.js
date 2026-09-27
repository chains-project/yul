const NUMERIC_RANGE = /^(-?\d+)-(-?\d+)$/;
const CHAR_RANGE = /^([A-Za-z])-([A-Za-z])$/;
const SINGLE_NUMBER = /^-?\d+$/;
const SINGLE_CHAR = /^[A-Za-z]$/;

function inclusiveRange(start, end) {
  const step = start <= end ? 1 : -1;
  const length = Math.abs(end - start) + 1;
  return Array.from({ length }, (_, i) => start + i * step);
}

function isLower(char) {
  return char === char.toLowerCase();
}

/**
 * Expand a range expression into an array of every value it spans.
 *
 * Supports inclusive numeric ranges ("1-10", "-3-3"), inclusive alphabetic
 * ranges of the same case ("a-z", "A-Z") in either direction ("z-a"), and
 * single values ("5", "c") which expand to a one-element array.
 *
 * @param {string} range
 * @returns {Array<number|string>}
 */
export function expandRange(range) {
  if (typeof range !== 'string') {
    throw new TypeError(`Expected a string, received ${typeof range}`);
  }

  const input = range.trim();

  const numeric = input.match(NUMERIC_RANGE);
  if (numeric) {
    return inclusiveRange(Number(numeric[1]), Number(numeric[2]));
  }

  const chars = input.match(CHAR_RANGE);
  if (chars) {
    const [, start, end] = chars;
    if (isLower(start) !== isLower(end)) {
      throw new RangeError(`Range endpoints must use the same case: "${range}"`);
    }
    return inclusiveRange(start.charCodeAt(0), end.charCodeAt(0)).map((code) =>
      String.fromCharCode(code)
    );
  }

  if (SINGLE_NUMBER.test(input)) {
    return [Number(input)];
  }

  if (SINGLE_CHAR.test(input)) {
    return [input];
  }

  throw new RangeError(`Invalid range: "${range}"`);
}

export default expandRange;
