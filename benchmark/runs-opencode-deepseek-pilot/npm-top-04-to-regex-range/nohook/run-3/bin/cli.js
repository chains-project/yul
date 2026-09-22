#!/usr/bin/env node
'use strict';

const toRegexRange = require('../');

function usage() {
  return [
    'Usage: range-to-regex <min> <max> [--anchor] [--capture]',
    '       range-to-regex <min>-<max> [--anchor] [--capture]',
    '',
    'Examples:',
    '  range-to-regex 1 100',
    '  range-to-regex 1-100 --anchor',
    '  range-to-regex -10-10 --capture',
  ].join('\n');
}

function parseArgs(argv) {
  const options = { anchor: false, capture: false };
  const positional = [];

  for (const arg of argv) {
    if (arg === '--anchor') options.anchor = true;
    else if (arg === '--capture') options.capture = true;
    else if (arg === '-h' || arg === '--help') options.help = true;
    else positional.push(arg);
  }

  return { positional, options };
}

function parseRange(positional) {
  if (positional.length === 2) {
    return [positional[0], positional[1]];
  }

  if (positional.length === 1) {
    const match = positional[0].match(/^(-?\d+)\s*-\s*(-?\d+)$/);
    if (!match) return null;
    return [match[1], match[2]];
  }

  return null;
}

function main(argv) {
  const { positional, options } = parseArgs(argv);

  if (options.help || positional.length === 0) {
    process.stdout.write(usage() + '\n');
    return positional.length === 0 && !options.help ? 1 : 0;
  }

  const range = parseRange(positional);
  if (!range) {
    process.stderr.write('Error: could not parse range. Expected "<min>-<max>" or "<min> <max>".\n');
    process.stderr.write(usage() + '\n');
    return 1;
  }

  try {
    process.stdout.write(toRegexRange(range[0], range[1], options) + '\n');
    return 0;
  } catch (err) {
    process.stderr.write(`Error: ${err.message}\n`);
    return 1;
  }
}

if (require.main === module) {
  process.exitCode = main(process.argv.slice(2));
}

module.exports = main;
