#!/usr/bin/env node
import { expandRange } from './expand-range.js';

const input = process.argv.slice(2).join(' ').trim();

if (!input) {
  console.error('Usage: expand-range <range>   e.g. "1-10" or "a-z"');
  process.exit(1);
}

try {
  console.log(JSON.stringify(expandRange(input)));
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
