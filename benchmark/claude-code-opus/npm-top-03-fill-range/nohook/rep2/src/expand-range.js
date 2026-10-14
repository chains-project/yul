const NUMERIC = /^(-?\d+)-(-?\d+)$/;
const ALPHA = /^([a-z])-([a-z])$|^([A-Z])-([A-Z])$/;

/**
 * Expand a range string into an array of every value in between (inclusive).
 *
 *   expandRange('1-5')   -> [1, 2, 3, 4, 5]
 *   expandRange('5-1')   -> [5, 4, 3, 2, 1]
 *   expandRange('-2-2')  -> [-2, -1, 0, 1, 2]
 *   expandRange('01-03') -> ['01', '02', '03']   (zero padding preserved)
 *   expandRange('a-e')   -> ['a', 'b', 'c', 'd', 'e']
 *   expandRange('1-10', 3) -> [1, 4, 7, 10]
 */
export function expandRange(range, step = 1) {
  if (typeof range !== 'string') {
    throw new TypeError(`Range must be a string, got ${typeof range}`);
  }
  if (!Number.isInteger(step) || step < 1) {
    throw new RangeError(`Step must be a positive integer, got ${step}`);
  }

  const input = range.trim();

  const num = input.match(NUMERIC);
  if (num) {
    const [, startStr, endStr] = num;
    const values = sequence(Number(startStr), Number(endStr), step);
    const width = padWidth(startStr, endStr);
    return width ? values.map((n) => pad(n, width)) : values;
  }

  const alpha = input.match(ALPHA);
  if (alpha) {
    const [start, end] = alpha.slice(1).filter(Boolean);
    return sequence(start.charCodeAt(0), end.charCodeAt(0), step).map((code) =>
      String.fromCharCode(code),
    );
  }

  throw new SyntaxError(
    `Invalid range "${range}". Expected "<int>-<int>" (e.g. "1-10") or "<letter>-<letter>" of the same case (e.g. "a-z").`,
  );
}

function sequence(start, end, step) {
  const dir = start <= end ? 1 : -1;
  const out = [];
  for (let i = start; dir > 0 ? i <= end : i >= end; i += step * dir) {
    out.push(i);
  }
  return out;
}

// Zero-pad only when an endpoint was written with a leading zero, e.g. "01-10".
function padWidth(...parts) {
  const padded = parts.some((p) => /^-?0\d/.test(p));
  return padded ? Math.max(...parts.map((p) => p.replace('-', '').length)) : 0;
}

function pad(n, width) {
  const digits = String(Math.abs(n)).padStart(width, '0');
  return n < 0 ? `-${digits}` : digits;
}
