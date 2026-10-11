#!/usr/bin/env node
import path from 'node:path';
import { watch, writeSnapshot, getEventsSince } from './watcher.js';

function parseArgs(argv) {
  const options = { mode: 'watch', dir: process.cwd(), snapshot: '.macos-watch-snapshot' };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--snapshot') {
      options.mode = 'snapshot';
    } else if (arg === '--since') {
      options.mode = 'since';
    } else if (arg === '--out') {
      options.snapshot = argv[i + 1];
      i += 1;
    } else if (!arg.startsWith('-')) {
      options.dir = path.resolve(arg);
    }
  }
  return options;
}

function log(error, events) {
  if (error) {
    console.error(error);
    process.exitCode = 1;
    return;
  }
  for (const event of events) {
    console.log(`${new Date().toISOString()}  ${event.type.padEnd(6)}  ${event.path}`);
  }
}

const options = parseArgs(process.argv.slice(2));

if (options.mode === 'snapshot') {
  await writeSnapshot(options.dir, options.snapshot);
  console.log(`Snapshot written to ${options.snapshot}`);
} else if (options.mode === 'since') {
  log(null, await getEventsSince(options.dir, options.snapshot));
} else {
  const subscription = await watch(options.dir, log);
  console.log(`Watching ${options.dir} (FSEvents). Press Ctrl+C to stop.`);

  const stop = async () => {
    await subscription.unsubscribe();
    process.exit(0);
  };
  process.on('SIGINT', stop);
  process.on('SIGTERM', stop);
}
