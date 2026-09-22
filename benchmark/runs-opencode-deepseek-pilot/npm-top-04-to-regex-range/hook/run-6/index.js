#!/usr/bin/env node

const toRegexRange = require('to-regex-range');

function parseRange(input) {
  const match = String(input).trim().match(/^(-?\d+)\s*-\s*(-?\d+)$/);
  if (!match) {
    throw new Error(`Invalid range "${input}". Expected a format like "1-100".`);
  }

  const min = Number(match[1]);
  const max = Number(match[2]);
  if (min > max) {
    throw new Error(`Invalid range "${input}". The start must be <= the end.`);
  }

  return { min, max };
}

function rangeToRegex(input) {
  const { min, max } = parseRange(input);
  return new RegExp(`^(${toRegexRange(min, max)})$`);
}

function main() {
  const range = process.argv[2] || '1-100';
  const regex = rangeToRegex(range);

  console.log(`Range: ${range}`);
  console.log(`Regex: ${regex}`);

  const values = process.argv.slice(3);
  for (const value of values) {
    console.log(`  ${value}: ${regex.test(value)}`);
  }
}

if (require.main === module) {
  main();
}

module.exports = { parseRange, rangeToRegex };
