#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { watchNative } from './watcher.js';

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    since: { type: 'string', short: 's' },
  },
});

const target = positionals[0] ?? process.cwd();
const options = {};
if (values.since !== undefined) options.since = Number(values.since);

const stop = watchNative(target, (event) => {
  const stamp = new Date().toISOString();
  const changes = Object.entries(event.changes)
    .filter(([, on]) => on)
    .map(([name]) => name)
    .join(',');
  const detail = changes ? ` [${changes}]` : '';
  const type = (event.type ?? 'unknown').padEnd(9);
  process.stdout.write(`${stamp} ${event.event.padEnd(12)} ${type} ${event.path}${detail}\n`);
}, options);

process.stdout.write(`Watching ${target} via FSEvents (Ctrl+C to stop)\n`);

const shutdown = async () => {
  await stop();
  process.exit(0);
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
