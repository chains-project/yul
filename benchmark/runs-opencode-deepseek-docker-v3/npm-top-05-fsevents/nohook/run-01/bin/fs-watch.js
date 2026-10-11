#!/usr/bin/env node
import { watch } from '../src/index.js';

const target = process.argv[2] ?? process.cwd();

const watcher = await watch(target);
console.log(`watching ${target} via ${watcher.name}`);

watcher.on('change', (event) => {
  console.log(JSON.stringify(event));
});

process.on('SIGINT', () => {
  watcher.stop();
  process.exit(0);
});
