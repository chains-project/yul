const NUMERIC = /^(-?\d+)-(-?\d+)$/;
const ALPHA = /^([a-zA-Z])-([a-zA-Z])$/;

/**
 * Expand a range string into an array of every value from start to end, inclusive.
 *
 *   expandRange('1-5')   // [1, 2, 3, 4, 5]
 *   expandRange('5-1')   // [5, 4, 3, 2, 1]
 *   expandRange('-2-2')  // [-2, -1, 0, 1, 2]
 *   expandRange('a-e')   // ['a', 'b', 'c', 'd', 'e']
 *   expandRange('1-10', { step: 3 }) // [1, 4, 7, 10]
 *
 * Numeric ranges return numbers; letter ranges return single-character strings.
 * Letter ranges must stay within one case ('a-z' or 'A-Z').
 */
export function expandRange(range, { step = 1 } = {}) {
  if (typeof range !== 'string') {
    throw new TypeError(`Range must be a string, got ${typeof range}`);
  }
  if (!Number.isInteger(step) || step <= 0) {
    throw new RangeError(`Step must be a positive integer, got ${step}`);
  }

  const input = range.trim();

  const numeric = input.match(NUMERIC);
  if (numeric) {
    return sequence(Number(numeric[1]), Number(numeric[2]), step);
  }

  const alpha = input.match(ALPHA);
  if (alpha) {
    const [, from, to] = alpha;
    if (isUpper(from) !== isUpper(to)) {
      throw new RangeError(`Letter range must not mix case: '${range}'`);
    }
    return sequence(from.charCodeAt(0), to.charCodeAt(0), step).map((code) =>
      String.fromCharCode(code),
    );
  }

  throw new SyntaxError(`Invalid range '${range}'; expected e.g. '1-10' or 'a-z'`);
}

function sequence(start, end, step) {
  const direction = start <= end ? 1 : -1;
  const values = [];
  for (let n = start; direction > 0 ? n <= end : n >= end; n += step * direction) {
    values.push(n);
  }
  return values;
}

function isUpper(char) {
  return char >= 'A' && char <= 'Z';
}
