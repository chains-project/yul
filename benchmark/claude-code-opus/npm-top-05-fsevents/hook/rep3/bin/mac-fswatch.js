#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { Watcher } from '../src/index.js';

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    json: { type: 'boolean', default: false },
    help: { type: 'boolean', short: 'h', default: false },
  },
});

if (values.help) {
  console.log('Usage: mac-fswatch [--json] [path]\n\nWatches path (default: cwd) recursively via FSEvents.');
  process.exit(0);
}

const watcher = new Watcher(positionals[0] ?? process.cwd());

watcher.on('change', (e) => {
  if (values.json) {
    console.log(JSON.stringify(e));
  } else {
    console.log(`${e.event.padEnd(12)} ${e.type.padEnd(9)} ${e.path}`);
  }
});

try {
  watcher.start();
} catch (err) {
  console.error(`mac-fswatch: ${err.message}`);
  process.exit(1);
}

console.error(`Watching ${watcher.root} (Ctrl-C to stop)`);

const shutdown = async () => {
  await watcher.stop();
  process.exit(0);
};
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
