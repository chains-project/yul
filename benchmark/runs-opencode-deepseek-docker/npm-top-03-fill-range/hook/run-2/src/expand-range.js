const NUMERIC = /^\d+$/;
const ALPHA = /^[a-zA-Z]$/;

export function expandRange(range) {
  if (typeof range !== "string") {
    throw new TypeError("range must be a string");
  }

  const parts = range.trim().split("-");
  if (parts.length !== 2 || parts[0] === "" || parts[1] === "") {
    throw new Error(`Invalid range: "${range}"`);
  }

  const [start, end] = parts.map((part) => part.trim());

  if (NUMERIC.test(start) && NUMERIC.test(end)) {
    const from = Number(start);
    const to = Number(end);
    return walk(from, to, from <= to ? 1 : -1, (n) => n);
  }

  if (ALPHA.test(start) && ALPHA.test(end)) {
    const from = start.codePointAt(0);
    const to = end.codePointAt(0);
    return walk(from, to, from <= to ? 1 : -1, (code) =>
      String.fromCodePoint(code)
    );
  }

  throw new Error(`Invalid range: "${range}"`);
}

function walk(from, to, step, convert) {
  const result = [];
  for (let value = from; step > 0 ? value <= to : value >= to; value += step) {
    result.push(convert(value));
  }
  return result;
}

export default expandRange;
