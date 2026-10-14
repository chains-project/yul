#!/usr/bin/env node
import { watch, isNative } from '../src/index.js';

const root = process.argv[2] ?? '.';

if (!isNative) {
  console.error('warning: native FSEvents unavailable, falling back to fs.watch');
}

const watcher = watch(root);
console.error(`watching ${root} (${isNative ? 'FSEvents' : 'fs.watch'})`);

watcher.on('change', ({ event, type, path, id }) => {
  console.log([id ?? '-', event, type, path].join('\t'));
});
watcher.on('error', (err) => {
  console.error(err);
  process.exitCode = 1;
});

const shutdown = async () => {
  await watcher.close();
  process.exit();
};
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
