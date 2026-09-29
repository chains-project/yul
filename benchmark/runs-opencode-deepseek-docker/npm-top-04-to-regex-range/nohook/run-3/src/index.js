function fixedWidthRange(lo, hi, width) {
  if (width === 1) {
    if (lo === 0 && hi === 9) return "\\d";
    return lo === hi ? String(lo) : `[${lo}-${hi}]`;
  }
  if (lo === 0 && hi === 10 ** width - 1) {
    return "\\d".repeat(width);
  }
  if (lo === hi) {
    return String(lo).padStart(width, "0");
  }

  const place = 10 ** (width - 1);
  const loFirst = Math.floor(lo / place);
  const hiFirst = Math.floor(hi / place);
  const loRest = lo % place;
  const hiRest = hi % place;

  if (loFirst === hiFirst) {
    return String(loFirst) + fixedWidthRange(loRest, hiRest, width - 1);
  }

  if (loRest === 0 && hiRest === place - 1) {
    return `[${loFirst}-${hiFirst}]` + "\\d".repeat(width - 1);
  }

  const parts = [];
  parts.push(String(loFirst) + fixedWidthRange(loRest, place - 1, width - 1));
  if (hiFirst - loFirst > 1) {
    parts.push(`[${loFirst + 1}-${hiFirst - 1}]` + "\\d".repeat(width - 1));
  }
  parts.push(String(hiFirst) + fixedWidthRange(0, hiRest, width - 1));

  return `(?:${parts.join("|")})`;
}

export function rangeToRegex(min, max, options = {}) {
  const { pad = false } = options;
  let lo = Math.trunc(min);
  let hi = Math.trunc(max);
  if (lo > hi) [lo, hi] = [hi, lo];

  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
    throw new TypeError("rangeToRegex expects finite numbers");
  }
  if (lo < 0) {
    throw new RangeError("rangeToRegex only supports non-negative integers");
  }

  const minLen = String(lo).length;
  const maxLen = String(hi).length;
  const parts = [];

  for (let width = minLen; width <= maxLen; width++) {
    const lower = Math.max(lo, width === 1 ? 0 : 10 ** (width - 1));
    const upper = Math.min(hi, 10 ** width - 1);
    if (lower > upper) continue;

    let body = fixedWidthRange(lower, upper, width);
    if (pad && width < maxLen) {
      body = `0{0,${maxLen - width}}${body}`;
    }
    parts.push(body);
  }

  return collapseRepeats(parts.length === 1 ? parts[0] : parts.join("|"));
}

function collapseRepeats(pattern) {
  return pattern.replace(/(?:\\d){2,}/g, (match) => `\\d{${match.length / 2}}`);
}

export function rangeRegExp(min, max, options = {}) {
  const { anchors = true, flags = "" } = options;
  const pattern = rangeToRegex(min, max, options);
  const source = anchors ? `^(?:${pattern})$` : pattern;
  return new RegExp(source, flags);
}

export function parseRange(input) {
  if (typeof input === "number") return { min: input, max: input };

  const match = String(input).trim().match(/^(\d+)\s*-\s*(\d+)$/);
  if (!match) {
    throw new Error(`Cannot parse range "${input}". Expected a "min-max" string like "1-100".`);
  }
  return { min: Number(match[1]), max: Number(match[2]) };
}

export function rangeStringToRegex(input, options = {}) {
  const { min, max } = parseRange(input);
  return rangeToRegex(min, max, options);
}

export function rangeStringToRegExp(input, options = {}) {
  const { min, max } = parseRange(input);
  return rangeRegExp(min, max, options);
}
