const NUMERIC = /^(-?\d+)-(-?\d+)$/;
const ALPHA = /^([a-z])-([a-z])$|^([A-Z])-([A-Z])$/;

/**
 * Expand a range string into an array of every value from start to end, inclusive.
 *
 *   expandRange('1-5')   // [1, 2, 3, 4, 5]
 *   expandRange('5-1')   // [5, 4, 3, 2, 1]
 *   expandRange('-2-2')  // [-2, -1, 0, 1, 2]
 *   expandRange('a-e')   // ['a', 'b', 'c', 'd', 'e']
 *
 * Letter ranges must be single characters of the same case.
 */
export function expandRange(range) {
  if (typeof range !== 'string') {
    throw new TypeError(`Expected a string, got ${typeof range}`);
  }
  const input = range.trim();

  const num = input.match(NUMERIC);
  if (num) {
    return sequence(Number(num[1]), Number(num[2]));
  }

  const alpha = input.match(ALPHA);
  if (alpha) {
    const start = alpha[1] ?? alpha[3];
    const end = alpha[2] ?? alpha[4];
    return sequence(start.charCodeAt(0), end.charCodeAt(0)).map((code) =>
      String.fromCharCode(code),
    );
  }

  throw new Error(`Invalid range: '${range}'. Expected e.g. '1-10' or 'a-z'.`);
}

function sequence(start, end) {
  const step = start <= end ? 1 : -1;
  const length = Math.abs(end - start) + 1;
  return Array.from({ length }, (_, i) => start + i * step);
}
