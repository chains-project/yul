const NUMERIC = /^(\d+)-(\d+)$/;
const ALPHA = /^([A-Za-z])-([A-Za-z])$/;

function range(start, end) {
  const step = start <= end ? 1 : -1;
  const result = [];
  for (let value = start; step > 0 ? value <= end : value >= end; value += step) {
    result.push(value);
  }
  return result;
}

export function expandRange(input) {
  if (typeof input !== "string") {
    throw new TypeError("Range must be a string, e.g. \"1-10\" or \"a-z\"");
  }

  const value = input.trim();

  const numeric = NUMERIC.exec(value);
  if (numeric) {
    return range(Number(numeric[1]), Number(numeric[2]));
  }

  const alpha = ALPHA.exec(value);
  if (alpha) {
    return range(alpha[1].codePointAt(0), alpha[2].codePointAt(0)).map((code) =>
      String.fromCharCode(code)
    );
  }

  throw new RangeError(`Invalid range: "${input}" (expected "1-10" or "a-z")`);
}
