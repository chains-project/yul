#!/usr/bin/env node
import { resolveRealPath } from './realpath.js';

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: resolve-realpath <path> [path...]');
  process.exit(2);
}

let failed = false;
for (const arg of args) {
  try {
    console.log(await resolveRealPath(arg));
  } catch (err) {
    failed = true;
    console.error(`resolve-realpath: ${arg}: ${err.code ?? err.message}`);
  }
}
process.exit(failed ? 1 : 0);
