const NUMERIC = /^(-?\d+)\s*-\s*(-?\d+)$/;
const ALPHA = /^([a-zA-Z])\s*-\s*([a-zA-Z])$/;

function sequence(start, end) {
  const step = start <= end ? 1 : -1;
  const length = Math.abs(end - start) + 1;
  return Array.from({ length }, (_, i) => start + i * step);
}

/**
 * Expand a range string into an array of every value in between, inclusive.
 *
 *   expandRange('1-5')  -> [1, 2, 3, 4, 5]
 *   expandRange('5-1')  -> [5, 4, 3, 2, 1]
 *   expandRange('-2-2') -> [-2, -1, 0, 1, 2]
 *   expandRange('a-e')  -> ['a', 'b', 'c', 'd', 'e']
 *
 * Letter ranges must be single characters of the same case.
 */
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
    const [, from, to] = alpha;
    const sameCase = (from === from.toLowerCase()) === (to === to.toLowerCase());
    if (!sameCase) {
      throw new RangeError(`Letter range must not mix case: "${input}"`);
    }
    return sequence(from.charCodeAt(0), to.charCodeAt(0)).map((code) =>
      String.fromCharCode(code),
    );
  }

  throw new SyntaxError(`Invalid range: "${input}" (expected e.g. "1-10" or "a-z")`);
}
