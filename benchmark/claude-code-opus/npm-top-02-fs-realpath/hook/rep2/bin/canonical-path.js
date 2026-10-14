#!/usr/bin/env node
import { canonicalPath } from '../src/realpath.js';

const args = process.argv.slice(2);
if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
  console.error('Usage: canonical-path <path> [path...]');
  process.exit(args.length === 0 ? 2 : 0);
}

let failed = false;
for (const arg of args) {
  try {
    console.log(await canonicalPath(arg));
  } catch (err) {
    console.error(`canonical-path: ${arg}: ${err.code ?? err.message}`);
    failed = true;
  }
}
process.exit(failed ? 1 : 0);
