const NUMERIC_RANGE = /^([+-]?\d+)\s*-\s*([+-]?\d+)$/;
const ALPHA_RANGE = /^([a-zA-Z])\s*-\s*([a-zA-Z])$/;

function rangeValues(start, end) {
  const step = start <= end ? 1 : -1;
  const values = [];
  for (let value = start; value !== end + step; value += step) {
    values.push(value);
  }
  return values;
}

export function expandRange(input) {
  if (typeof input !== "string") {
    throw new TypeError(`Range must be a string, received ${typeof input}`);
  }

  const value = input.trim();
  if (value === "") {
    throw new RangeError("Range must not be empty");
  }

  const numeric = value.match(NUMERIC_RANGE);
  if (numeric) {
    return rangeValues(Number(numeric[1]), Number(numeric[2]));
  }

  const alpha = value.match(ALPHA_RANGE);
  if (alpha) {
    const start = alpha[1].codePointAt(0);
    const end = alpha[2].codePointAt(0);
    const sameCase =
      (alpha[1] === alpha[1].toUpperCase()) ===
      (alpha[2] === alpha[2].toUpperCase());
    if (!sameCase) {
      throw new RangeError("Range endpoints must use the same letter case");
    }
    return rangeValues(start, end).map((code) => String.fromCodePoint(code));
  }

  throw new RangeError(
    `Invalid range: "${input}". Expected forms like "1-10" or "a-z"`,
  );
}
