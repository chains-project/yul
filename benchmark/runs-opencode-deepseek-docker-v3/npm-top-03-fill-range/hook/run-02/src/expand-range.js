const NUMERIC = /^-?\d+$/;
const LETTER = /^[A-Za-z]$/;
const RANGE = /^(-?\d+|[A-Za-z])-(-?\d+|[A-Za-z])$/;

function numericRange(start, end) {
  const step = start <= end ? 1 : -1;
  const values = [];
  for (let i = start; step > 0 ? i <= end : i >= end; i += step) {
    values.push(i);
  }
  return values;
}

function letterRange(start, end) {
  const from = start.charCodeAt(0);
  const to = end.charCodeAt(0);
  const step = from <= to ? 1 : -1;
  const values = [];
  for (let i = from; step > 0 ? i <= to : i >= to; i += step) {
    values.push(String.fromCharCode(i));
  }
  return values;
}

export function expandRange(range) {
  if (typeof range !== "string") {
    throw new TypeError("range must be a string");
  }

  const match = RANGE.exec(range.trim());
  if (!match) {
    throw new Error(`Invalid range: ${range}`);
  }

  const [, start, end] = match;

  if (NUMERIC.test(start) && NUMERIC.test(end)) {
    return numericRange(Number(start), Number(end));
  }

  if (LETTER.test(start) && LETTER.test(end)) {
    return letterRange(start, end);
  }

  throw new Error(`Range endpoints must both be numeric or both be letters: ${range}`);
}
