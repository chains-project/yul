#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { watch, nativeAvailable } from './index.js';

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    recursive: { type: 'boolean', short: 'r', default: true },
    latency: { type: 'string' },
    debounce: { type: 'string' },
    since: { type: 'string' },
  },
});

const target = positionals[0] ?? process.cwd();
const options = {
  recursive: values.recursive,
  latency: values.latency != null ? Number(values.latency) : undefined,
  debounce: values.debounce != null ? Number(values.debounce) : undefined,
  since: values.since != null ? Number(values.since) : undefined,
};

console.log(
  `Watching ${target} via ${nativeAvailable() ? 'native FSEvents' : 'fs.watch (fallback)'}`,
);

const watcher = watch(target, options);
watcher.on('event', (event) => {
  const detail = event.flagNames.length ? ` [${event.flagNames.join(', ')}]` : '';
  console.log(`${event.event}\t${event.path}${detail}`);
});

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => {
    watcher.close();
    process.exit(0);
  });
}
