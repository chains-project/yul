const INTEGER_RANGE = /^(-?\d+)\s*-\s*(-?\d+)$/;
const CHAR_RANGE = /^([a-zA-Z])\s*-\s*([a-zA-Z])$/;
const SINGLE_VALUE = /^(-?\d+)$/;
const SINGLE_CHAR = /^[a-zA-Z]$/;

function sequence(start, end) {
  const step = start <= end ? 1 : -1;
  const length = Math.abs(end - start) + 1;
  return Array.from({ length }, (_, i) => start + i * step);
}

export function expandRange(input) {
  if (typeof input !== "string") {
    throw new TypeError("expandRange expects a string");
  }

  const value = input.trim();

  const integerRange = value.match(INTEGER_RANGE);
  if (integerRange) {
    return sequence(Number(integerRange[1]), Number(integerRange[2]));
  }

  const charRange = value.match(CHAR_RANGE);
  if (charRange) {
    const start = charRange[1].codePointAt(0);
    const end = charRange[2].codePointAt(0);
    return sequence(start, end).map((code) => String.fromCodePoint(code));
  }

  if (SINGLE_VALUE.test(value)) {
    return [Number(value)];
  }

  if (SINGLE_CHAR.test(value)) {
    return [value];
  }

  throw new SyntaxError(`Invalid range: "${input}"`);
}
