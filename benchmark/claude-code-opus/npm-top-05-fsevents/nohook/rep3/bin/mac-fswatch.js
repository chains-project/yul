#!/usr/bin/env node
import { resolve } from 'node:path';
import { watch } from '../src/index.js';

const root = resolve(process.argv[2] ?? '.');
const json = process.argv.includes('--json');

const stop = watch(root, (e) => {
  if (json) {
    console.log(JSON.stringify(e));
  } else {
    console.log(`${e.event.padEnd(12)} ${e.type.padEnd(9)} ${e.path}`);
  }
});

console.error(`Watching ${root} (Ctrl+C to stop)`);

const shutdown = async () => {
  await stop();
  process.exit(0);
};
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
