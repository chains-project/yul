#!/usr/bin/env node
import { resolveRealPath } from './realpath.js';

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: realpath-resolve <path> [path...]');
  process.exit(2);
}

let failed = false;
for (const arg of args) {
  try {
    console.log(await resolveRealPath(arg));
  } catch (err) {
    console.error(`${arg}: ${err.code ?? err.message}`);
    failed = true;
  }
}
process.exitCode = failed ? 1 : 0;
