#!/usr/bin/env node
import { expandRange } from '../src/expand-range.js';

const [range, stepArg] = process.argv.slice(2);

if (!range) {
  console.error('Usage: expand-range <range> [step]   e.g. expand-range 1-10, expand-range a-z 2');
  process.exit(1);
}

try {
  const step = stepArg === undefined ? 1 : Number(stepArg);
  console.log(JSON.stringify(expandRange(range, { step })));
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
