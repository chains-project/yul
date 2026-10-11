#!/usr/bin/env node
import { parseRange, toRegexSource } from '../src/range-to-regex.js';

const USAGE = `Usage: range-to-regex <min-max> [number]

Prints a regular expression matching any integer in the given range.
If a number is supplied, reports whether it matches.

Examples:
  range-to-regex 1-100
  range-to-regex 1-100 42`;

function main(argv) {
  if (argv.length === 0 || argv.includes('-h') || argv.includes('--help')) {
    console.log(USAGE);
    return argv.length === 0 ? 1 : 0;
  }

  const [range, number] = argv;
  let source;
  try {
    const { min, max } = parseRange(range);
    source = toRegexSource(min, max);
  } catch (error) {
    console.error(`error: ${error.message}`);
    return 1;
  }

  console.log(source);

  if (number !== undefined) {
    if (!/^\d+$/.test(number)) {
      console.error(`error: "${number}" is not a non-negative integer`);
      return 1;
    }
    const matches = new RegExp(source).test(number);
    console.log(matches ? `match: ${number}` : `no match: ${number}`);
    return matches ? 0 : 1;
  }

  return 0;
}

process.exitCode = main(process.argv.slice(2));
