#!/usr/bin/env node
import { resolveRealPath } from '../src/index.js';

const paths = process.argv.slice(2);

if (paths.length === 0) {
  console.error('Usage: realpath-resolver <path> [path...]');
  process.exit(1);
}

let failed = false;

for (const input of paths) {
  try {
    console.log(await resolveRealPath(input));
  } catch (err) {
    failed = true;
    console.error(`realpath-resolver: ${input}: ${err.message}`);
  }
}

process.exitCode = failed ? 1 : 0;
