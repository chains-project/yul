function charClass(low, high) {
  if (low === high) return String(low);
  if (low === 0 && high === 9) return "\\d";
  return `[${low}-${high}]`;
}

function fixedLength(low, high) {
  const remaining = low.length - 1;
  if (remaining === 0) return charClass(Number(low), Number(high));
  if (low === high) return low;

  if (low[0] === high[0]) {
    return low[0] + fixedLength(low.slice(1), high.slice(1));
  }

  const parts = [
    low[0] + fixedLength(low.slice(1), "9".repeat(remaining)),
  ];

  const midLow = Number(low[0]) + 1;
  const midHigh = Number(high[0]) - 1;
  if (midLow <= midHigh) {
    parts.push(charClass(midLow, midHigh) + `\\d{${remaining}}`);
  }

  parts.push(high[0] + fixedLength("0".repeat(remaining), high.slice(1)));

  return `(?:${parts.join("|")})`;
}

function positiveRange(min, max) {
  const parts = [];
  const minLength = String(min).length;
  const maxLength = String(max).length;

  for (let length = minLength; length <= maxLength; length += 1) {
    const low = length === 1 ? Math.max(min, 0) : Math.max(min, 10 ** (length - 1));
    const high = Math.min(max, 10 ** length - 1);
    if (low > high) continue;
    parts.push(fixedLength(String(low), String(high)));
  }

  return parts.length === 1 ? parts[0] : `(?:${parts.join("|")})`;
}

export function rangeToRegexSource(input, maxArg) {
  let min;
  let max;

  if (typeof input === "string") {
    const match = input.trim().match(/^(-?\d+)\s*-\s*(-?\d+)$/);
    if (!match) {
      throw new TypeError(
        `Invalid range "${input}". Expected a string like "1-100".`,
      );
    }
    min = Number(match[1]);
    max = Number(match[2]);
  } else {
    min = Number(input);
    max = Number(maxArg);
  }

  if (!Number.isInteger(min) || !Number.isInteger(max)) {
    throw new TypeError("Range bounds must be integers.");
  }

  if (min > max) [min, max] = [max, min];

  const parts = [];

  if (min < 0) {
    const negativeHigh = Math.min(max, -1);
    parts.push("-" + positiveRange(-negativeHigh, -min));
  }

  const nonNegativeLow = Math.max(min, 0);
  if (max >= nonNegativeLow) {
    parts.push(positiveRange(nonNegativeLow, max));
  }

  return parts.length === 1 ? parts[0] : `(?:${parts.join("|")})`;
}

export function rangeToRegex(input, maxArg) {
  return new RegExp(`^(?:${rangeToRegexSource(input, maxArg)})$`);
}

export default rangeToRegex;
