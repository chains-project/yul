#!/usr/bin/env node
import { resolveRealPath } from '../src/realpath.js';

const args = process.argv.slice(2);
if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
  console.error('Usage: resolve-realpath <path> [path...]');
  process.exit(args.length === 0 ? 1 : 0);
}

let failed = false;
for (const arg of args) {
  try {
    console.log(await resolveRealPath(arg));
  } catch (err) {
    failed = true;
    const reason = {
      ENOENT: 'no such file or directory',
      ELOOP: 'too many levels of symbolic links',
      EACCES: 'permission denied',
      ENOTDIR: 'a path component is not a directory',
    }[err.code] ?? err.message;
    console.error(`resolve-realpath: ${arg}: ${reason}`);
  }
}
process.exit(failed ? 1 : 0);
