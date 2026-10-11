const DIGIT = '[0-9]';

function fillByNines(value, count) {
  const s = String(value);
  const keep = Math.max(0, s.length - count);
  return Number(s.slice(0, keep) + '9'.repeat(count));
}

function fillByZeros(value, count) {
  const s = String(value);
  const keep = Math.max(0, s.length - count);
  return Number(s.slice(0, keep) + '0'.repeat(count));
}

function splitToRanges(min, max) {
  const stops = new Set([max]);

  let nines = 1;
  let stop = fillByNines(min, nines);
  while (min <= stop && stop <= max) {
    stops.add(stop);
    nines += 1;
    stop = fillByNines(min, nines);
  }

  let zeros = 1;
  stop = fillByZeros(max, zeros) - 1;
  while (min <= stop && stop <= max) {
    stops.add(stop);
    zeros += 1;
    stop = fillByZeros(max, zeros) - 1;
  }

  return [...stops].sort((a, b) => a - b);
}

function rangeToPattern(start, stop) {
  const a = String(start);
  const b = String(stop);
  let pattern = '';
  let anyDigits = 0;

  const flush = () => {
    if (anyDigits === 1) pattern += DIGIT;
    else if (anyDigits > 1) pattern += `${DIGIT}{${anyDigits}}`;
    anyDigits = 0;
  };

  for (let i = 0; i < a.length; i += 1) {
    const startDigit = a[i];
    const stopDigit = b[i];

    if (startDigit === '0' && stopDigit === '9') {
      anyDigits += 1;
      continue;
    }

    flush();

    if (startDigit === stopDigit) {
      pattern += startDigit;
    } else {
      pattern += `[${startDigit}-${stopDigit}]`;
    }
  }

  flush();
  return pattern;
}

export function rangeToRegexSource(min, max) {
  if (!Number.isInteger(min) || !Number.isInteger(max)) {
    throw new TypeError('range bounds must be integers');
  }

  if (min > max) [min, max] = [max, min];
  if (min === max) return String(min);

  const patterns = [];
  let start = min;
  for (const stop of splitToRanges(min, max)) {
    patterns.push(rangeToPattern(start, stop));
    start = stop + 1;
  }
  return patterns.join('|');
}

export function rangeToRegex(min, max, options = {}) {
  const { anchors = true } = options;
  const body = `(?:${rangeToRegexSource(min, max)})`;
  return new RegExp(anchors ? `^${body}$` : body);
}

export function parseRange(input) {
  const match = /^(\d+)\s*-\s*(\d+)$/.exec(String(input).trim());
  if (!match) throw new Error(`invalid numeric range: "${input}"`);
  return [Number(match[1]), Number(match[2])];
}

export function rangeToRegexFromString(input, options) {
  return rangeToRegex(...parseRange(input), options);
}
