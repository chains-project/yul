#!/usr/bin/env node
import { watch, isNative } from './watch.js';

const target = process.argv[2] ?? process.cwd();

console.log(`watching ${target} (${isNative ? 'fsevents' : 'fs.watch fallback'})`);

const stop = watch(target, (info) => {
  const changes = Object.entries(info.changes)
    .filter(([, value]) => value)
    .map(([key]) => key)
    .join(',');
  const detail = changes ? ` [${changes}]` : '';
  console.log(`${info.event.padEnd(9)} ${info.path}${detail}`);
});

const shutdown = () => {
  stop();
  process.exit(0);
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
