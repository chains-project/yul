import toRegexRange from 'to-regex-range';

function rangeToRegex(input) {
  const match = String(input).trim().match(/^(-?\d+)\s*-\s*(-?\d+)$/);
  if (!match) {
    throw new Error(`Invalid range "${input}". Expected a numeric range like "1-100".`);
  }

  const [, min, max] = match;
  return new RegExp(`^(${toRegexRange(min, max)})$`);
}

const input = process.argv[2] || '1-100';
const regex = rangeToRegex(input);

console.log(regex.source);

export { rangeToRegex };
