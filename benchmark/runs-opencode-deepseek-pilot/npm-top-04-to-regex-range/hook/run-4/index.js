#!/usr/bin/env node
import toRegexRange from 'to-regex-range';

export function rangeToRegex(range, { anchors = true } = {}) {
  const match = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/.exec(String(range));
  if (!match) {
    throw new Error(`Invalid range: "${range}". Expected a value like "1-100".`);
  }

  const [, start, end] = match;
  const source = toRegexRange(start, end, { capture: false });
  return new RegExp(anchors ? `^(?:${source})$` : source);
}

function main() {
  const range = process.argv[2] ?? '1-100';

  try {
    const regex = rangeToRegex(range);
    console.log(regex.source);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
