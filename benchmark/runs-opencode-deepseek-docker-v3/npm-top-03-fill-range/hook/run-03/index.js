#!/usr/bin/env node

const RANGE_RE = /^(.+?)\s*-\s*(.+)$/;

export function expandRange(range) {
  if (typeof range !== "string") {
    throw new TypeError("range must be a string");
  }

  const match = RANGE_RE.exec(range.trim());
  if (!match) {
    throw new TypeError(`invalid range: "${range}"`);
  }

  const start = match[1].trim();
  const end = match[2].trim();

  if (/^-?\d+$/.test(start) && /^-?\d+$/.test(end)) {
    return numericRange(Number(start), Number(end));
  }

  if (isSingleLetter(start) && isSingleLetter(end)) {
    if (isUpper(start) !== isUpper(end)) {
      throw new TypeError(`letter range must use the same case: "${range}"`);
    }
    return charRange(start, end);
  }

  throw new TypeError(`unsupported range: "${range}"`);
}

function numericRange(start, end) {
  const step = start <= end ? 1 : -1;
  const length = Math.abs(end - start) + 1;
  return Array.from({ length }, (_, i) => start + i * step);
}

function charRange(start, end) {
  const step = start <= end ? 1 : -1;
  const a = start.codePointAt(0);
  const b = end.codePointAt(0);
  const length = Math.abs(b - a) + 1;
  return Array.from({ length }, (_, i) => String.fromCodePoint(a + i * step));
}

function isSingleLetter(value) {
  return /^[A-Za-z]$/.test(value);
}

function isUpper(value) {
  return value >= "A" && value <= "Z";
}

function main(argv) {
  if (argv.length === 0) {
    console.error("usage: expand-range <start>-<end> [more ranges...]");
    process.exit(1);
  }

  for (const arg of argv) {
    console.log(JSON.stringify(expandRange(arg)));
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main(process.argv.slice(2));
}
