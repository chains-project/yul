const NUMERIC_RANGE = /^(-?\d+)-(-?\d+)$/;
const ALPHA_RANGE = /^([a-zA-Z])-([a-zA-Z])$/;

function buildNumeric(start, end, step) {
  const direction = start <= end ? 1 : -1;
  const stride = Math.abs(step) * direction;
  const out = [];
  if (direction === 1) {
    for (let i = start; i <= end; i += stride) out.push(i);
  } else {
    for (let i = start; i >= end; i += stride) out.push(i);
  }
  return out;
}

function buildAlpha(start, end, step) {
  const a = start.codePointAt(0);
  const b = end.codePointAt(0);
  return buildNumeric(a, b, step).map((code) => String.fromCodePoint(code));
}

function expandToken(token, step) {
  const trimmed = token.trim();
  if (trimmed === "") throw new Error("Empty range token");

  const numMatch = trimmed.match(NUMERIC_RANGE);
  if (numMatch) {
    return buildNumeric(Number(numMatch[1]), Number(numMatch[2]), step);
  }

  const alphaMatch = trimmed.match(ALPHA_RANGE);
  if (alphaMatch) {
    return buildAlpha(alphaMatch[1], alphaMatch[2], step);
  }

  throw new Error(`Invalid range: "${token}"`);
}

export function expandRange(input, options = {}) {
  if (typeof input !== "string") {
    throw new TypeError("Range must be a string");
  }

  const { step = 1, maxSize = 10000 } = options;
  if (!Number.isInteger(step) || step === 0) {
    throw new RangeError("step must be a non-zero integer");
  }

  const values = input
    .split(",")
    .flatMap((token) => expandToken(token, step));

  if (values.length > maxSize) {
    throw new RangeError(`Range expands to ${values.length} values (max ${maxSize})`);
  }

  return values;
}

export default expandRange;
