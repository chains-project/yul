#!/usr/bin/env node
'use strict';

const toRegexRange = require('../');

const usage = 'Usage: to-regex-range <min-max>\n       to-regex-range <min> <max>';

const fail = message => {
  console.error(message);
  console.error(usage);
  process.exit(1);
};

const parse = args => {
  if (args.length === 1) {
    let input = args[0].trim();
    let match = /^(-?\d+)\s*-\s*(-?\d+)$/.exec(input);

    if (match) {
      return [Number(match[1]), Number(match[2])];
    }

    if (/^-?\d+$/.test(input)) {
      return [Number(input)];
    }

    fail(`to-regex-range: unable to parse range "${input}"`);
  }

  if (args.length === 2) {
    if (!/^-?\d+$/.test(args[0]) || !/^-?\d+$/.test(args[1])) {
      fail(`to-regex-range: expected two numbers, received "${args.join(' ')}"`);
    }
    return [Number(args[0]), Number(args[1])];
  }

  fail('to-regex-range: expected a range or two numbers');
};

const main = () => {
  let args = process.argv.slice(2);
  if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
    console.log(usage);
    process.exit(args.length === 0 ? 1 : 0);
  }

  let [min, max] = parse(args);
  let result = toRegexRange(min, max);

  console.log(result);
  return result;
};

if (require.main === module) {
  main();
}

module.exports = main;
