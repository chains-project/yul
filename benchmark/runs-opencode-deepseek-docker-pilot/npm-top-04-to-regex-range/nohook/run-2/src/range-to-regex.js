function hasTopLevelAlternation(source) {
  let depth = 0;
  for (let i = 0; i < source.length; i++) {
    const ch = source[i];
    if (ch === '\\') {
      i++;
      continue;
    }
    if (ch === '[' || ch === '(') {
      depth++;
      continue;
    }
    if (ch === ']' || ch === ')') {
      depth--;
      continue;
    }
    if (ch === '|' && depth === 0) {
      return true;
    }
  }
  return false;
}

function wrap(source) {
  return hasTopLevelAlternation(source) ? `(?:${source})` : source;
}

function digitClass(low, high) {
  if (low === high) {
    return String(low);
  }
  if (low === 0 && high === 9) {
    return '\\d';
  }
  return `[${low}-${high}]`;
}

function anyDigit(count) {
  return count === 1 ? '\\d' : `\\d{${count}}`;
}

function gen(lo, hi) {
  const length = lo.length;
  if (lo === hi) {
    return lo;
  }

  let prefixLength = 0;
  while (prefixLength < length && lo[prefixLength] === hi[prefixLength]) {
    prefixLength++;
  }
  if (prefixLength > 0) {
    const prefix = lo.slice(0, prefixLength);
    return prefix + wrap(gen(lo.slice(prefixLength), hi.slice(prefixLength)));
  }

  const lowDigit = Number(lo[0]);
  const highDigit = Number(hi[0]);
  const restLength = length - 1;
  if (restLength === 0) {
    return digitClass(lowDigit, highDigit);
  }

  const loRest = lo.slice(1);
  const hiRest = hi.slice(1);
  const zeros = '0'.repeat(restLength);
  const nines = '9'.repeat(restLength);
  const parts = [
    lo[0] + wrap(gen(loRest, nines))
  ];

  if (highDigit - lowDigit > 1) {
    parts.push(digitClass(lowDigit + 1, highDigit - 1) + anyDigit(restLength));
  }

  parts.push(hi[0] + wrap(gen(zeros, hiRest)));
  return wrap(parts.join('|'));
}

function nonNegativeRange(min, max) {
  const parts = [];
  const highest = String(max).length;
  for (let length = String(min).length; length <= highest; length++) {
    const low = Math.max(min, length === 1 ? 0 : 10 ** (length - 1));
    const high = Math.min(max, 10 ** length - 1);
    if (low > high) {
      continue;
    }
    parts.push(gen(String(low), String(high)));
  }
  return wrap(parts.join('|'));
}

export function rangeToRegex(min, max = min) {
  if (!Number.isInteger(min) || !Number.isInteger(max)) {
    throw new TypeError('rangeToRegex: expected integer bounds');
  }
  if (min > max) {
    [min, max] = [max, min];
  }

  const parts = [];
  if (min < 0) {
    const magnitudeHigh = Math.abs(min);
    const magnitudeLow = max < 0 ? Math.abs(max) : 1;
    if (magnitudeLow <= magnitudeHigh) {
      parts.push('-' + wrap(nonNegativeRange(magnitudeLow, magnitudeHigh)));
    }
  }

  const nonNegativeMin = Math.max(min, 0);
  if (nonNegativeMin <= max) {
    parts.push(nonNegativeRange(nonNegativeMin, max));
  }

  return wrap(parts.join('|'));
}

export function rangeToRegexAnchored(min, max = min) {
  return `^(?:${rangeToRegex(min, max)})$`;
}

export default rangeToRegex;
