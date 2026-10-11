#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { rangeToRegex } from './range-to-regex.js';

const USAGE = `Usage: range-to-regex <range> [options]

Convert a numeric range into a regular expression that matches any
number in that range.

Arguments:
  range             A range like "1-100", or a single value like "42".

Options:
  -s, --source      Print only the regex source (no slashes/flags).
  -t, --test <n>    Test whether <n> matches the generated regex.
  -h, --help        Show this help.

Examples:
  range-to-regex 1-100
  range-to-regex 1-100 --source
  range-to-regex 1-100 --test 77`;

function main(argv) {
  let parsed;
  try {
    parsed = parseArgs({
      args: argv,
      options: {
        source: { type: 'boolean', short: 's' },
        test: { type: 'string', short: 't' },
        help: { type: 'boolean', short: 'h' }
      },
      allowPositionals: true
    });
  } catch (error) {
    console.error(error.message);
    console.error(USAGE);
    process.exitCode = 1;
    return;
  }

  const { values, positionals } = parsed;

  if (values.help || positionals.length === 0) {
    console.log(USAGE);
    return;
  }

  if (positionals.length > 1) {
    console.error(`Expected a single range, got ${positionals.length}.`);
    console.error(USAGE);
    process.exitCode = 1;
    return;
  }

  let regex;
  try {
    regex = rangeToRegex(positionals[0]);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exitCode = 1;
    return;
  }

  if (values.test !== undefined) {
    const match = regex.test(values.test);
    console.log(`${values.test} ${match ? 'matches' : 'does not match'} ${regex}`);
    process.exitCode = match ? 0 : 1;
    return;
  }

  console.log(values.source ? regex.source : regex);
}

main(process.argv.slice(2));
