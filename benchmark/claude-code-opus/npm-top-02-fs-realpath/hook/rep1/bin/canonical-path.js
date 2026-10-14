#!/usr/bin/env node
import { realpath } from '../src/realpath.js';

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: canonical-path <path> [path...]');
  process.exit(2);
}

let failed = false;
for (const arg of args) {
  try {
    console.log(await realpath(arg));
  } catch (err) {
    console.error(`canonical-path: ${arg}: ${err.code ?? err.message}`);
    failed = true;
  }
}
process.exit(failed ? 1 : 0);
