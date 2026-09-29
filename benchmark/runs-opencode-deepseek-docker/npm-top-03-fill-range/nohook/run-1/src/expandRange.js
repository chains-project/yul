const INTEGER = /^-?\d+$/;
const LETTER = /^[A-Za-z]$/;

function expandNumeric(start, end) {
  const from = Number(start);
  const to = Number(end);
  const step = from <= to ? 1 : -1;

  const values = [];
  for (let i = from; step > 0 ? i <= to : i >= to; i += step) {
    values.push(i);
  }
  return values;
}

function expandLetters(start, end) {
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
  if (typeof range !== 'string') {
    throw new TypeError('Range must be a string, e.g. "1-10" or "a-z"');
  }

  const match = range.trim().match(/^([^-]+)-(.+)$/);
  if (!match) {
    throw new Error(`Invalid range: "${range}"`);
  }

  const [, start, end] = match;

  if (INTEGER.test(start) && INTEGER.test(end)) {
    return expandNumeric(start, end);
  }

  if (LETTER.test(start) && LETTER.test(end)) {
    return expandLetters(start, end);
  }

  throw new Error(`Invalid range: "${range}" (use "1-10", "-3-3" or "a-z")`);
}
