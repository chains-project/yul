#!/usr/bin/env node
'use strict';

const path = require('path');
const { watch, isSupported } = require('../src');

if (!isSupported()) {
  console.error('fswatch-macos: native FSEvents is only available on macOS.');
  process.exit(1);
}

const target = path.resolve(process.argv[2] || '.');
console.error(`Watching ${target} (Ctrl+C to stop)`);

const stop = watch(target, (e) => {
  console.log(JSON.stringify({ event: e.event, type: e.type, path: e.path, changes: e.changes }));
});

process.on('SIGINT', async () => {
  await stop();
  process.exit(0);
});
