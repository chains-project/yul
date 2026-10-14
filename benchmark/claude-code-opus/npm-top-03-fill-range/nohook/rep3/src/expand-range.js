const NUMERIC = /^(-?\d+)-(-?\d+)$/;
const ALPHA = /^([a-zA-Z])-([a-zA-Z])$/;

function step(start, end) {
  return start <= end ? 1 : -1;
}

/**
 * Expand a range string into an array of every value from start to end, inclusive.
 *
 *   expandRange('1-5')  // [1, 2, 3, 4, 5]
 *   expandRange('5-1')  // [5, 4, 3, 2, 1]
 *   expandRange('-2-2') // [-2, -1, 0, 1, 2]
 *   expandRange('a-e')  // ['a', 'b', 'c', 'd', 'e']
 *   expandRange('E-A')  // ['E', 'D', 'C', 'B', 'A']
 */
export function expandRange(range) {
  if (typeof range !== 'string') {
    throw new TypeError(`Range must be a string, got ${typeof range}`);
  }
  const input = range.trim();

  const numeric = input.match(NUMERIC);
  if (numeric) {
    const start = Number(numeric[1]);
    const end = Number(numeric[2]);
    const dir = step(start, end);
    const result = [];
    for (let n = start; n !== end + dir; n += dir) result.push(n);
    return result;
  }

  const alpha = input.match(ALPHA);
  if (alpha) {
    const [, from, to] = alpha;
    const fromIsUpper = from === from.toUpperCase();
    const toIsUpper = to === to.toUpperCase();
    if (fromIsUpper !== toIsUpper) {
      throw new RangeError(`Letter range must not mix cases: "${range}"`);
    }
    const start = from.charCodeAt(0);
    const end = to.charCodeAt(0);
    const dir = step(start, end);
    const result = [];
    for (let c = start; c !== end + dir; c += dir) result.push(String.fromCharCode(c));
    return result;
  }

  throw new SyntaxError(
    `Invalid range "${range}". Expected "<int>-<int>" (e.g. "1-10") or "<letter>-<letter>" (e.g. "a-z").`
  );
}
