const fsevents = require('fsevents');

const watchPath = process.argv[2] || process.cwd();

const stop = fsevents.watch(watchPath, (path, flags, id) => {
  const info = fsevents.getInfo(path, flags, id);
  console.log(`${info.event}: ${path} (type: ${info.type})`);
});

console.log(`Watching ${watchPath} for changes... (Ctrl+C to stop)`);

process.on('SIGINT', () => {
  stop();
  process.exit(0);
});
