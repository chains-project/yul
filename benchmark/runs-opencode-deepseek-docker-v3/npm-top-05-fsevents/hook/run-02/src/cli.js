#!/usr/bin/env node
import { watch, native } from './index.js';

const target = process.argv[2] ?? process.cwd();

if (!native) {
  console.error(
    'Native FSEvents unavailable. This tool must run on macOS with the "fsevents" addon installed.',
  );
  process.exit(1);
}

console.log(`Watching ${target} for native FSEvents notifications...`);

const stop = watch(target, (event) => {
  const stamp = new Date().toISOString();
  console.log(`${stamp}  ${event.event.padEnd(12)} ${event.path}`);
});

function shutdown() {
  stop();
  process.exit(0);
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
