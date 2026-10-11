const MAX_SAFE = Number.MAX_SAFE_INTEGER;

/**
 * Convert an inclusive integer range into a regular expression source string.
 *
 * The returned pattern matches the numbers in [min, max] written in standard
 * decimal form (no leading zeros) and matches them as a whole.
 *
 * @param {number} min
 * @param {number} max
 * @returns {string} regex source, without ^ or $ anchors
 */
export function rangeToRegex(min, max) {
  if (!Number.isInteger(min) || !Number.isInteger(max)) {
    throw new TypeError('range bounds must be integers');
  }
  if (min < 0 || max < 0) {
    throw new RangeError('range bounds must be non-negative');
  }
  if (min > MAX_SAFE || max > MAX_SAFE) {
    throw new RangeError('range bounds must not exceed Number.MAX_SAFE_INTEGER');
  }

  if (min > max) [min, max] = [max, min];

  const parts = [];
  const minLength = String(min).length;
  const maxLength = String(max).length;

  for (let length = minLength; length <= maxLength; length += 1) {
    const segmentLow = length === 1 ? 0 : 10 ** (length - 1);
    const segmentHigh = 10 ** length - 1;
    const low = Math.max(min, segmentLow);
    const high = Math.min(max, segmentHigh);
    if (low > high) continue;
    parts.push(buildFixedLength(low, high, length));
  }

  return parts.length === 1 ? parts[0] : `(${parts.join('|')})`;
}

/**
 * Return a RegExp that matches the whole range.
 *
 * @param {number} min
 * @param {number} max
 * @param {string} [flags]
 * @returns {RegExp}
 */
export function rangeToRegExp(min, max, flags) {
  return new RegExp(`^(?:${rangeToRegex(min, max)})$`, flags);
}

function buildFixedLength(low, high, length) {
  return build(String(low).padStart(length, '0'), String(high).padStart(length, '0'));
}

function build(low, high) {
  const length = low.length;
  if (low === high) return low;
  if (low === '0'.repeat(length) && high === '9'.repeat(length)) {
    return '[0-9]'.repeat(length);
  }
  if (length === 1) return charClass(low, high);

  if (low[0] === high[0]) {
    return low[0] + build(low.slice(1), high.slice(1));
  }

  const parts = [low[0] + build(low.slice(1), '9'.repeat(length - 1))];

  const middleLow = Number(low[0]) + 1;
  const middleHigh = Number(high[0]) - 1;
  if (middleLow <= middleHigh) {
    parts.push(charClass(middleLow, middleHigh) + '[0-9]'.repeat(length - 1));
  }

  parts.push(high[0] + build('0'.repeat(length - 1), high.slice(1)));

  return `(${parts.join('|')})`;
}

function charClass(low, high) {
  if (low === high) return String(low);
  if (Number(low) === 0 && Number(high) === 9) return '[0-9]';
  return `[${low}-${high}]`;
}
