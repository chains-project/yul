#!/usr/bin/env node
import process from 'node:process';
import { watch as fsWatch } from 'node:fs';

const target = process.argv[2] ?? process.cwd();

async function startFsevents(path) {
  const mod = await import('fsevents');
  const fsevents = mod.default ?? mod;
  return fsevents.watch(path, (changedPath, flags, id) => {
    const info = fsevents.getInfo(changedPath, flags, id);
    const type = info.type ? ` (${info.type})` : '';
    console.log(`${info.event}\t${info.path}${type}`);
  });
}

function startFallback(path) {
  console.warn(
    `[warn] fsevents is macOS-only; falling back to fs.watch on ${process.platform}`,
  );
  const watcher = fsWatch(path, { recursive: true }, (eventType, filename) => {
    console.log(`${eventType}\t${filename ?? path}`);
  });
  return () => watcher.close();
}

let stop;
if (process.platform === 'darwin') {
  try {
    stop = await startFsevents(target);
  } catch (err) {
    console.warn(`[warn] fsevents unavailable (${err.message}); using fs.watch`);
    stop = startFallback(target);
  }
} else {
  stop = startFallback(target);
}

console.log(`Watching ${target}... (Ctrl+C to stop)`);

function shutdown() {
  stop();
  process.exit(0);
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
