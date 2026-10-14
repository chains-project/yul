#!/usr/bin/env node
import { expandRange } from './expand-range.js';

const [range] = process.argv.slice(2);

if (!range) {
  console.error('Usage: expand-range <range>   e.g. expand-range 1-10, expand-range a-z');
  process.exit(1);
}

try {
  console.log(JSON.stringify(expandRange(range)));
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
