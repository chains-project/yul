#!/usr/bin/env node
import { rangeToRegex } from './index.js';

const args = process.argv.slice(2);
const anchored = !args.includes('--no-anchor');
const range = args.find((a) => !a.startsWith('--'));

if (!range) {
  console.error('Usage: range-to-regex <min>-<max> [--no-anchor]');
  process.exit(1);
}

try {
  console.log(rangeToRegex(range, { anchored }).source);
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
