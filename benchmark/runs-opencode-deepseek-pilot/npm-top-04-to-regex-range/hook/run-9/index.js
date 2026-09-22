import toRegexRange from 'to-regex-range';

const RANGE_RE = /^(-?\d+)\s*-\s*(-?\d+)$/;

export function rangeToRegex(range, options = {}) {
  const match = RANGE_RE.exec(String(range).trim());
  if (!match) {
    throw new Error(`Invalid numeric range: ${range}`);
  }

  const [, min, max] = match;
  const source = toRegexRange(min, max, { capture: true, ...options });
  return new RegExp(`^${source}$`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const input = process.argv[2] || '1-100';
  const regex = rangeToRegex(input);
  console.log(`Range: ${input}`);
  console.log(`Regex: ${regex}`);
}
