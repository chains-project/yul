function charClass(low, high) {
  return low === high ? String(low) : `[${low}-${high}]`;
}

function anyDigits(count) {
  if (count === 0) return "";
  return count === 1 ? "[0-9]" : `[0-9]{${count}}`;
}

function group(alternatives) {
  return alternatives.length === 1
    ? alternatives[0]
    : `(?:${alternatives.join("|")})`;
}

function toAlternatives(low, high) {
  if (low === high) return [low];

  const length = low.length;
  let shared = 0;
  while (shared < length && low[shared] === high[shared]) shared += 1;

  if (shared > 0) {
    const prefix = low.slice(0, shared);
    return toAlternatives(low.slice(shared), high.slice(shared)).map(
      (alternative) => prefix + alternative,
    );
  }

  const first = Number(low[0]);
  const last = Number(high[0]);

  if (length === 1) return [charClass(first, last)];

  const tail = anyDigits(length - 1);
  const alternatives = [];

  for (const rest of toAlternatives(low.slice(1), "9".repeat(length - 1))) {
    alternatives.push(low[0] + rest);
  }

  if (last - first > 1) {
    alternatives.push(`[${first + 1}-${last - 1}]${tail}`);
  }

  for (const rest of toAlternatives("0".repeat(length - 1), high.slice(1))) {
    alternatives.push(high[0] + rest);
  }

  return alternatives;
}

export function parseRange(input) {
  const match = /^\s*(\d+)\s*-\s*(\d+)\s*$/.exec(String(input));
  if (!match) {
    throw new RangeError(
      `expected a range like "1-100", received "${input}"`,
    );
  }
  return [match[1], match[2]];
}

export function rangeToRegex(min, max, options = {}) {
  const { anchors = true } = options;

  min = BigInt(min);
  max = BigInt(max);

  if (min < 0n) {
    throw new RangeError("rangeToRegex only supports non-negative ranges");
  }
  if (min > max) {
    throw new RangeError(`invalid range: ${min} is greater than ${max}`);
  }

  const firstDigits = min.toString().length;
  const lastDigits = max.toString().length;
  const branches = [];

  for (let digits = firstDigits; digits <= lastDigits; digits += 1) {
    const lower = digits === 1 ? 0n : 10n ** BigInt(digits - 1);
    const upper = 10n ** BigInt(digits) - 1n;
    const low = min > lower ? min : lower;
    const high = max < upper ? max : upper;

    if (low > high) continue;

    branches.push(group(toAlternatives(low.toString(), high.toString())));
  }

  const body = branches.join("|");
  return anchors ? `^(?:${body})$` : body;
}

export function rangeToRegexFromString(input, options) {
  return rangeToRegex(...parseRange(input), options);
}
