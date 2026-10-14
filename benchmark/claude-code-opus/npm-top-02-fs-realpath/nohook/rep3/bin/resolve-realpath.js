#!/usr/bin/env node
'use strict';

const { resolveRealpath } = require('../src/realpath');

async function main(args) {
  if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
    console.error('Usage: resolve-realpath <path> [<path> ...]');
    return args.length === 0 ? 2 : 0;
  }

  let status = 0;
  for (const p of args) {
    try {
      console.log(await resolveRealpath(p));
    } catch (err) {
      console.error(`resolve-realpath: ${p}: ${err.code || err.message}`);
      status = 1;
    }
  }
  return status;
}

main(process.argv.slice(2)).then((code) => {
  process.exitCode = code;
});
