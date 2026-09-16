const fsevents = require('fsevents');
const path = require('path');

const watchedPath = process.argv[2] || path.resolve('.');

const stopWatching = fsevents(watchedPath, (filePath, flags, id) => {
  const eventName = getEventName(flags);
  console.log(`${filePath} — ${eventName}`);
});

console.log(`Watching: ${watchedPath}`);

process.on('SIGINT', () => {
  stopWatching();
  console.log('Stopped watching.');
  process.exit(0);
});

function getEventName(flags) {
  const names = [];
  if (flags & 0x00000001) names.push('IS_FILE');
  if (flags & 0x00000002) names.push('IS_DIR');
  if (flags & 0x00000004) names.push('IS_LAST_ROOT');
  if (flags & 0x00000010) names.push('NEEDS_RECURSION');
  if (flags & 0x10000000) names.push('CREATED');
  if (flags & 0x20000000) names.push('MODIFIED');
  if (flags & 0x40000000) names.push('ITEM_REMOVED');
  if (flags & 0x80000000) names.push('ITEM_RENAMED');
  if (flags & 0x00000100) names.push('ITEM_CHOWN');
  if (flags & 0x00000200) names.push('ITEM_EXTEND');
  if (flags & 0x00000400) names.push('ITEM_FORK');
  if (flags & 0x00000800) names.push('ITEM_UNLINK');
  if (flags & 0x00001000) names.push('ITEM_RELINK');
  if (flags & 0x00000020) names.push('ROOT_CHANGED');
  return names.length ? names.join(', ') : 'UNKNOWN';
}