#!/usr/bin/env node
import { watch } from '../src/index.js';

const target = process.argv[2] ?? process.cwd();

let watcher;
try {
  watcher = watch(target);
} catch (err) {
  console.error(err.message);
  process.exit(1);
}

console.error(`Watching ${target} (Ctrl+C to stop)`);

watcher.on('change', ({ event, type, path }) => {
  console.log(`${new Date().toISOString()}  ${event.padEnd(12)} ${type.padEnd(9)} ${path}`);
});

const shutdown = async () => {
  await watcher.close();
  process.exit(0);
};
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
