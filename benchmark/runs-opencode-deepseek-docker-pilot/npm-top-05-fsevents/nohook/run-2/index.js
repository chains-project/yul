'use strict';

const path = require('node:path');

let fsevents;
try {
  fsevents = require('fsevents');
} catch {
  fsevents = null;
}

function watch(target, onEvent) {
  if (!fsevents) {
    throw new Error(
      'fsevents is unavailable. It is macOS-only; run "npm install" on Darwin to build the native binding.'
    );
  }

  const dir = path.resolve(target);
  const handle = fsevents.watch(dir, (changedPath, flags, id) => {
    onEvent(fsevents.getInfo(changedPath, flags, id));
  });

  return () => fsevents.stop(handle);
}

if (require.main === module) {
  const target = process.argv[2] || process.cwd();
  console.log(`Watching ${path.resolve(target)} (Ctrl+C to stop)`);

  const stop = watch(target, (info) => {
    const changed = Object.keys(info.changes).filter((key) => info.changes[key]);
    const suffix = changed.length ? ` [${changed.join(', ')}]` : '';
    console.log(`${info.event.padEnd(8)} ${info.type.padEnd(9)} ${info.path}${suffix}`);
  });

  process.on('SIGINT', () => {
    stop();
    process.exit(0);
  });
}

module.exports = { watch };
