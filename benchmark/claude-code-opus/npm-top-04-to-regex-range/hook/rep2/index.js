#!/usr/bin/env node
import toRegexRange from 'to-regex-range';
import { fileURLToPath } from 'node:url';

/**
 * Convert a range string like "1-100" into a RegExp matching any integer in it.
 * Negative bounds are supported, e.g. "-10-10" or "-20--5".
 */
export function rangeToRegex(range) {
  const match = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/.exec(range);
  if (!match) {
    throw new Error(`Invalid range "${range}". Expected format: "min-max", e.g. "1-100".`);
  }
  const [min, max] = [Number(match[1]), Number(match[2])];
  return new RegExp(`^${toRegexRange(Math.min(min, max), Math.max(min, max))}$`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const input = process.argv[2];
  if (!input) {
    console.error('Usage: range-regex <min-max>   e.g. range-regex 1-100');
    process.exit(1);
  }
  try {
    console.log(rangeToRegex(input).source);
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}
