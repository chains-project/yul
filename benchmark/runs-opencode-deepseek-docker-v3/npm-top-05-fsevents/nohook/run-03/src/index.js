#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { watch, usingNativeFSEvents } from './watcher.js';

const target = path.resolve(process.argv[2] ?? process.cwd());

if (!isDirectory(target)) {
  console.error(`Not a directory: ${target}`);
  process.exit(1);
}

console.error(
  `Watching ${target} using ${usingNativeFSEvents ? 'native FSEvents' : 'fs.watch fallback'}`,
);

const watcher = watch(target);

watcher.on('all', (info) => {
  console.log(JSON.stringify({ event: info.event, path: info.path }));
});

process.on('SIGINT', () => {
  watcher.close();
  process.exit(0);
});

function isDirectory(p) {
  try {
    return fs.statSync(p).isDirectory();
  } catch {
    return false;
  }
}
