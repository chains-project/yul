#!/usr/bin/env node
import { parseRange, rangeToRegex } from '../src/range-to-regex.js';

const usage = 'Usage: range-to-regex <min>-<max>\nExample: range-to-regex 1-100';

const input = process.argv[2];
if (!input || input === '-h' || input === '--help') {
  console.log(usage);
  process.exit(input ? 0 : 1);
}

try {
  const [min, max] = parseRange(input);
  console.log(rangeToRegex(min, max).source);
} catch (error) {
  console.error(error.message);
  console.error(usage);
  process.exit(1);
}
