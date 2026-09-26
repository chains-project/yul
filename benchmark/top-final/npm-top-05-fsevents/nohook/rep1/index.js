if (process.platform !== 'darwin') {
  console.error('fs-watch-macos only works on macOS (uses the native FSEvents API).');
  process.exit(1);
}

const fsevents = require('fsevents');

const watchPath = process.argv[2] || process.cwd();

const stop = fsevents.watch(watchPath, (path, flags, info) => {
  const { event, type } = fsevents.getInfo(path, flags);
  console.log(`[${event}] ${type} ${path}`);
});

process.on('SIGINT', () => {
  stop();
  process.exit(0);
});

console.log(`Watching ${watchPath} for changes (Ctrl+C to stop)...`);
