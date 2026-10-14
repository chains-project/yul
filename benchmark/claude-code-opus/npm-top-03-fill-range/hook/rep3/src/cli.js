#!/usr/bin/env node
import { expandRange } from './expandRange.js';

const [range] = process.argv.slice(2);

if (!range) {
  console.error('Usage: expand-range <range>   e.g. expand-range 1-10');
  process.exit(1);
}

try {
  console.log(expandRange(range).join(' '));
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
