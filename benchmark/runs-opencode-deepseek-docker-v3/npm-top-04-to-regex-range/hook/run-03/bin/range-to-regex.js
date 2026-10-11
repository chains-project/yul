#!/usr/bin/env node
import { rangeToRegex } from '../src/range-to-regex.js';

const USAGE = `Usage:
  range-to-regex <min>-<max>
  range-to-regex <min> <max>

Examples:
  range-to-regex 1-100
  range-to-regex 200 300`;

const args = process.argv.slice(2);

if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
  console.log(USAGE);
  process.exit(args.length === 0 ? 1 : 0);
}

let min;
let max;

if (args.length === 1) {
  const match = /^(\d+)\s*-\s*(\d+)$/.exec(args[0]);
  if (!match) {
    console.error(`Invalid range: "${args[0]}"`);
    console.error(USAGE);
    process.exit(1);
  }
  min = Number(match[1]);
  max = Number(match[2]);
} else {
  min = Number(args[0]);
  max = Number(args[1]);
}

try {
  console.log(rangeToRegex(min, max));
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
