const ANY_DIGIT = '[0-9]';

function anyDigits(count) {
  if (count === 0) return '';
  if (count === 1) return ANY_DIGIT;
  return `${ANY_DIGIT}{${count}}`;
}

function charClass(low, high) {
  if (low === high) return String(low);
  if (high - low === 1) return `[${low}${high}]`;
  return `[${low}-${high}]`;
}

function group(pattern) {
  return pattern.includes('|') ? `(?:${pattern})` : pattern;
}

function fixedWidthRegex(low, high) {
  if (low === high) return low;
  if (low.length === 1) return charClass(Number(low), Number(high));
  if (/^0+$/.test(low) && /^9+$/.test(high)) return anyDigits(low.length);

  let i = 0;
  while (i < low.length && low[i] === high[i]) i += 1;

  const prefix = low.slice(0, i);
  const lowSuffix = low.slice(i);
  const highSuffix = high.slice(i);
  const remaining = lowSuffix.length - 1;
  const parts = [];

  const lowSub =
    remaining === 0
      ? String(lowSuffix[0])
      : `${lowSuffix[0]}${group(fixedWidthRegex(lowSuffix.slice(1), '9'.repeat(remaining)))}`;
  parts.push(lowSub);

  const middleLow = Number(lowSuffix[0]) + 1;
  const middleHigh = Number(highSuffix[0]) - 1;
  if (middleLow <= middleHigh) {
    parts.push(charClass(middleLow, middleHigh) + anyDigits(remaining));
  }

  const highSub =
    remaining === 0
      ? String(highSuffix[0])
      : `${highSuffix[0]}${group(fixedWidthRegex('0'.repeat(remaining), highSuffix.slice(1)))}`;
  parts.push(highSub);

  const body = parts.join('|');
  if (prefix === '') return body;
  return parts.length === 1 ? prefix + body : `${prefix}(?:${body})`;
}

function assertRange(min, max) {
  if (!Number.isInteger(min) || !Number.isInteger(max)) {
    throw new TypeError('range bounds must be integers');
  }
  if (min < 0 || max < 0) {
    throw new RangeError('range bounds must be non-negative');
  }
  if (min > max) {
    throw new RangeError(`invalid range: ${min} > ${max}`);
  }
}

export function toRegexSource(min, max) {
  assertRange(min, max);

  const maxDigits = String(max).length;
  const alternatives = [];

  for (let digits = String(min).length; digits <= maxDigits; digits += 1) {
    const lower = Math.max(min, digits === 1 ? 0 : 10 ** (digits - 1));
    const upper = Math.min(max, 10 ** digits - 1);
    if (lower > upper) continue;

    alternatives.push(fixedWidthRegex(String(lower), String(upper)));
  }

  if (alternatives.length === 1) {
    return `^(?:${alternatives[0]})$`;
  }
  return `^(?:${alternatives.join('|')})$`;
}

export function rangeToRegex(min, max, flags) {
  return new RegExp(toRegexSource(min, max), flags);
}

export function parseRange(range) {
  if (typeof range !== 'string') {
    throw new TypeError('range must be a string like "1-100"');
  }

  const match = /^\s*(\d+)\s*-\s*(\d+)\s*$/.exec(range);
  if (!match) {
    throw new SyntaxError(`invalid range: "${range}" (expected "min-max")`);
  }

  return { min: Number(match[1]), max: Number(match[2]) };
}

export function rangeToRegexFromString(range, flags) {
  const { min, max } = parseRange(range);
  return rangeToRegex(min, max, flags);
}
