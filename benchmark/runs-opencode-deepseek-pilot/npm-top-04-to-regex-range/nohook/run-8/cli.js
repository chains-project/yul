#!/usr/bin/env node

'use strict';

const toRegexRange = require('./index.js');

const help = `Usage: range-to-regex <range> [options]

Convert a numeric range into a single regular expression that matches any
number in that range.

Arguments:
  <range>            A range such as "1-100", "-5-5" or "10..20".

Options:
  -c, --capture      Wrap the result in a capturing group.
  -s, --shorthand    Use \\d instead of [0-9].
      --strict-zeros Keep leading zeros strict (disable relaxed zeros).
      --no-wrap      Do not wrap the result in a non-capturing group.
  -h, --help         Show this help message.

Examples:
  $ range-to-regex 1-100
  $ range-to-regex -5-5
  $ range-to-regex 1-1000 --shorthand
`;

const parseRange = input => {
  let match = /^(-?\d+)\s*(?:-|\.\.)\s*(-?\d+)$/.exec(String(input).trim());
  if (!match) {
    throw new Error(`invalid range: "${input}" (expected e.g. "1-100")`);
  }
  return [Number(match[1]), Number(match[2])];
};

const main = argv => {
  let args = argv.slice(2);
  let options = {};
  let range;

  for (let i = 0; i < args.length; i++) {
    let arg = args[i];

    switch (arg) {
      case '-h':
      case '--help':
        process.stdout.write(help);
        return 0;
      case '-c':
      case '--capture':
        options.capture = true;
        break;
      case '-s':
      case '--shorthand':
        options.shorthand = true;
        break;
      case '--strict-zeros':
        options.strictZeros = true;
        break;
      case '--no-wrap':
        options.wrap = false;
        break;
      default:
        if (arg.startsWith('-') && !/^-?\d/.test(arg)) {
          process.stderr.write(`unknown option: ${arg}\n`);
          return 1;
        }
        if (range === undefined) {
          range = arg;
        } else {
          process.stderr.write(`unexpected argument: ${arg}\n`);
          return 1;
        }
    }
  }

  if (range === undefined) {
    process.stderr.write(help);
    return 1;
  }

  try {
    let [min, max] = parseRange(range);
    process.stdout.write(toRegexRange(min, max, options) + '\n');
    return 0;
  } catch (err) {
    process.stderr.write(`${err.message}\n`);
    return 1;
  }
};

if (require.main === module) {
  process.exitCode = main(process.argv);
}

module.exports = { main, parseRange };
