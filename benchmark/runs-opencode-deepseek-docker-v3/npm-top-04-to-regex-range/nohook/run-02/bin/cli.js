#!/usr/bin/env node
import { rangeToRegex } from '../src/index.js';

const USAGE = `Usage: range-regex <range> [--match <value>]

Convert a numeric range into a single regular expression.

Arguments:
  <range>            Inclusive range, e.g. "1-100" or "1..100"

Options:
  -m, --match <n>    Test a value against the generated expression
  -h, --help         Show this help

Examples:
  range-regex 1-100
  range-regex 1-100 --match 42
`;

function main(argv) {
  const args = [...argv];
  let matchValue;

  const matchIndex = args.findIndex((arg) => arg === '-m' || arg === '--match');
  if (matchIndex !== -1) {
    matchValue = args.splice(matchIndex, 2)[1];
    if (matchValue === undefined) {
      throw new Error('Missing value for --match');
    }
  }

  if (args.includes('-h') || args.includes('--help')) {
    process.stdout.write(USAGE);
    return 0;
  }

  const range = args[0];
  if (!range) {
    process.stderr.write(USAGE);
    return 1;
  }

  const source = rangeToRegex(range);
  process.stdout.write(`${source}\n`);

  if (matchValue !== undefined) {
    const re = new RegExp(`^(?:${source})$`);
    process.stdout.write(`${re.test(matchValue) ? 'match' : 'no match'}\n`);
  }

  return 0;
}

try {
  process.exitCode = main(process.argv.slice(2));
} catch (error) {
  process.stderr.write(`range-regex: ${error.message}\n`);
  process.exitCode = 1;
}
