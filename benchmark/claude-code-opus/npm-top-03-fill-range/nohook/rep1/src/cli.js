#!/usr/bin/env node
import { expandRange } from './expandRange.js';

const args = process.argv.slice(2);

if (args.length === 0) {
  console.error('Usage: expand-range <range> [range...]   e.g. 1-10 a-z');
  process.exit(1);
}

try {
  for (const arg of args) {
    console.log(JSON.stringify(expandRange(arg)));
  }
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
