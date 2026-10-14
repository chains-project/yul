#!/usr/bin/env node
import { resolve } from 'node:path';
import { watch } from '../src/index.js';

const target = resolve(process.argv[2] ?? '.');

let stop;
try {
  stop = watch(target, (e) => {
    console.log(JSON.stringify({ event: e.event, type: e.type, path: e.path, flags: e.flags, id: String(e.id) }));
  });
} catch (err) {
  console.error(`mac-fswatch: ${err.message}`);
  process.exit(1);
}

console.error(`Watching ${target} (Ctrl+C to stop)`);

process.on('SIGINT', async () => {
  await stop();
  process.exit(0);
});
