const path = require('node:path');

if (process.platform !== 'darwin') {
  throw new Error('This tool relies on fsevents and only runs on macOS.');
}

const fsevents = require('fsevents');

const watchPath = process.argv[2] || process.cwd();

const stop = fsevents.watch(path.resolve(watchPath), (file, flags, id) => {
  const info = fsevents.getInfo(file, flags, id);
  console.log(`[${info.event}] ${info.type} ${file}`);
});

process.on('SIGINT', () => {
  stop();
  process.exit(0);
});

console.log(`Watching ${watchPath} for changes (Ctrl+C to stop)...`);
