/**
 * Expand a range string into an array of values.
 *
 *   expandRange('1-5')   -> [1, 2, 3, 4, 5]
 *   expandRange('5-1')   -> [5, 4, 3, 2, 1]
 *   expandRange('-2-2')  -> [-2, -1, 0, 1, 2]
 *   expandRange('a-e')   -> ['a', 'b', 'c', 'd', 'e']
 *   expandRange('Z-W')   -> ['Z', 'Y', 'X', 'W']
 *
 * Numeric endpoints are integers (optionally negative). Letter endpoints are
 * single characters of the same case.
 */
const NUMERIC = /^(-?\d+)-(-?\d+)$/;
const ALPHA = /^([a-zA-Z])-([a-zA-Z])$/;

export function expandRange(input) {
  if (typeof input !== 'string') {
    throw new TypeError(`Range must be a string, got ${typeof input}`);
  }
  const range = input.trim();

  const num = range.match(NUMERIC);
  if (num) {
    return sequence(Number(num[1]), Number(num[2]));
  }

  const alpha = range.match(ALPHA);
  if (alpha) {
    const [, start, end] = alpha;
    if (isUpper(start) !== isUpper(end)) {
      throw new RangeError(`Letter range must not mix case: "${input}"`);
    }
    return sequence(start.charCodeAt(0), end.charCodeAt(0)).map((code) =>
      String.fromCharCode(code),
    );
  }

  throw new SyntaxError(
    `Invalid range "${input}". Expected e.g. "1-10" or "a-z".`,
  );
}

function sequence(start, end) {
  const step = start <= end ? 1 : -1;
  const length = Math.abs(end - start) + 1;
  return Array.from({ length }, (_, i) => start + i * step);
}

function isUpper(ch) {
  return ch >= 'A' && ch <= 'Z';
}
