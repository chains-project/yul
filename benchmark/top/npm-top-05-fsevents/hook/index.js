const fsevents = require('fsevents');
const path = require('path');

const watchPath = process.argv[2] || process.cwd();

const stop = fsevents.watch(path.resolve(watchPath), (file, flags, id) => {
  const info = fsevents.getInfo(file, flags, id);
  console.log(`[${info.event}] ${file} (${info.type})`);
});

console.log(`Watching ${watchPath} for changes... (Ctrl+C to stop)`);

process.on('SIGINT', () => {
  stop();
  process.exit(0);
});
