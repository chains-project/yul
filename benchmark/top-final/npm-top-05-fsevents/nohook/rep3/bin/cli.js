#!/usr/bin/env node
'use strict';

const path = require('path');
const { watch } = require('../index.js');

const target = path.resolve(process.argv[2] || '.');

console.log(`Watching ${target} for filesystem changes (Ctrl+C to stop)...`);

const stop = watch(target, (filePath, flags, info) => {
  console.log(JSON.stringify({ path: filePath, flags, info }));
});

process.on('SIGINT', async () => {
  await stop();
  process.exit(0);
});
