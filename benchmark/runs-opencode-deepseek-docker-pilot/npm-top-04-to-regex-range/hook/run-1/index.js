function toInteger(value, name) {
  const number = typeof value === "string" ? Number(value) : value;
  if (typeof number !== "number" || !Number.isInteger(number)) {
    throw new TypeError(`${name} must be an integer, received ${JSON.stringify(value)}`);
  }
  if (!Number.isSafeInteger(number)) {
    throw new RangeError(`${name} must be a safe integer`);
  }
  return number;
}

function digitSuffix(count) {
  if (count <= 0) return "";
  if (count === 1) return "\\d";
  return `\\d{${count}}`;
}

function digitClassRange(low, high) {
  if (low === high) return low;
  if (low === "0" && high === "9") return "\\d";
  return `[${low}-${high}]`;
}

function alternatives(low, high) {
  const length = low.length;
  if (length === 0) return [""];
  if (length === 1) return [digitClassRange(low, high)];
  if (low === high) return [low];
  if (low === "0".repeat(length) && high === "9".repeat(length)) {
    return [digitSuffix(length)];
  }
  if (low === `1${"0".repeat(length - 1)}` && high === "9".repeat(length)) {
    return [`[1-9]${digitSuffix(length - 1)}`];
  }
  if (low[0] === high[0]) {
    return alternatives(low.slice(1), high.slice(1)).map((suffix) => low[0] + suffix);
  }

  const out = [];
  const firstLow = low[0];
  const firstHigh = high[0];
  const lowDigit = Number(firstLow);
  const highDigit = Number(firstHigh);

  for (const suffix of alternatives(low.slice(1), "9".repeat(length - 1))) {
    out.push(firstLow + suffix);
  }
  if (highDigit - lowDigit > 1) {
    out.push(`[${lowDigit + 1}-${highDigit - 1}]${digitSuffix(length - 1)}`);
  }
  for (const suffix of alternatives("0".repeat(length - 1), high.slice(1))) {
    out.push(firstHigh + suffix);
  }
  return out;
}

function splitTrailingDigits(alternative) {
  if (alternative.endsWith("\\d")) {
    return { base: alternative.slice(0, -2), count: 1 };
  }
  const match = /\\d\{(\d+)\}$/.exec(alternative);
  if (match) {
    return { base: alternative.slice(0, match.index), count: Number(match[1]) };
  }
  return { base: alternative, count: 0 };
}

function digitRun(start, end) {
  if (start === 0 && end === 1) return "\\d?";
  if (start === 0) return `\\d{0,${end}}`;
  if (start === end) return start === 1 ? "\\d" : `\\d{${start}}`;
  return `\\d{${start},${end}}`;
}

function factorAlternatives(list) {
  const countsByBase = new Map();
  for (const alternative of list) {
    const { base, count } = splitTrailingDigits(alternative);
    if (base === "") continue;
    if (!countsByBase.has(base)) countsByBase.set(base, new Set());
    countsByBase.get(base).add(count);
  }

  const out = [];
  const emitted = new Set();
  const ungrouped = new Set();

  for (const alternative of list) {
    const { base } = splitTrailingDigits(alternative);
    if (base === "") {
      if (!ungrouped.has(alternative)) {
        ungrouped.add(alternative);
        out.push(alternative);
      }
      continue;
    }
    if (emitted.has(base)) continue;
    emitted.add(base);

    const counts = [...countsByBase.get(base)].sort((a, b) => a - b);
    let start = counts[0];
    let end = counts[0];
    const runs = [];
    for (let i = 1; i < counts.length; i++) {
      if (counts[i] === end + 1) {
        end = counts[i];
      } else {
        runs.push([start, end]);
        start = counts[i];
        end = counts[i];
      }
    }
    runs.push([start, end]);

    for (const [runStart, runEnd] of runs) {
      if (runStart === 0 && runEnd === 0) out.push(base);
      else out.push(base + digitRun(runStart, runEnd));
    }
  }

  return out;
}

/**
 * Build a regular expression source string that matches any integer in
 * `[min, max]`. The result is anchored with `^...$` unless `anchor` is false.
 */
export function rangeToRegex(min, max, options = {}) {
  const { anchor = true } = options;

  let low = toInteger(min, "min");
  let high = toInteger(max, "max");
  if (low > high) [low, high] = [high, low];
  if (low < 0) throw new RangeError("range bounds must be non-negative");

  const lowStr = String(low);
  const highStr = String(high);
  const collected = [];

  for (let length = lowStr.length; length <= highStr.length; length++) {
    const lower = length === 1 ? low : Math.max(low, 10 ** (length - 1));
    const upper = Math.min(high, 10 ** length - 1);
    if (lower > upper) continue;
    collected.push(...alternatives(String(lower), String(upper)));
  }

  const factored = factorAlternatives(collected);
  const core = factored.length === 1 ? factored[0] : factored.join("|");
  return anchor ? `^(?:${core})$` : core;
}

/** Parse a string such as "1-100" into `[1, 100]`. */
export function parseRange(input) {
  const match = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/.exec(String(input));
  if (!match) throw new TypeError(`invalid numeric range: ${JSON.stringify(input)}`);
  return [Number(match[1]), Number(match[2])];
}

/** Return true when `value` falls inside the given range. */
export function matches(range, value, options = {}) {
  const [min, max] = typeof range === "string" ? parseRange(range) : range;
  const regex = new RegExp(rangeToRegex(min, max, { ...options, anchor: true }));
  return regex.test(String(value));
}

export default rangeToRegex;
