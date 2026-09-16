const fsevents = require('fsevents');
const path = require('path');

// Watch the current directory (or a specified path)
const watchPath = process.argv[2] || process.cwd();
const resolvedPath = path.resolve(watchPath);

console.log(`Watching path: ${resolvedPath}`);

const stopWatching = fsevents(resolvedPath, (filePath, flags, id) => {
  const eventNames = {
    1: 'NONE',
    2: 'FILE',
    4: 'DIR',
    8: 'INODE_META',
    16: 'ITEM_NAME',
    32: 'ITEM_SIZE',
    64: 'ITEM_EXTEND',
    128: 'ITEM_ATTR_CHANGE',
    256: 'ITEM_CLONE',
    512: 'ITEM_RENAME',
    1024: 'ITEM_LINK',
    2048: 'ITEM_ZERO',
    4096: 'ITEM_REMOVE',
    8192: 'ITEM_RESTORE'
  };

  const flagNames = Object.entries(eventNames)
    .filter(([num]) => flags & parseInt(num))
    .map(([, name]) => name)
    .join(', ');

  console.log(`[${new Date().toISOString()}] ${path.basename(filePath)} (${flagNames})`);
});

console.log('Press Ctrl+C to stop watching...');

process.on('SIGINT', () => {
  stopWatching();
  console.log('\nStopped watching.');
  process.exit(0);
});