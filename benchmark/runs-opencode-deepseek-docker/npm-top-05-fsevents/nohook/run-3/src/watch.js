import { createRequire } from 'node:module';
import { watch as watchFallback } from 'node:fs';

const require = createRequire(import.meta.url);

function loadFsevents() {
  try {
    return require('fsevents');
  } catch {
    return null;
  }
}

const fsevents = loadFsevents();

export const isNative = fsevents !== null;

/**
 * Watch a directory for filesystem changes.
 *
 * On macOS this uses the native FSEvents API, which reports low-level
 * events (created, removed, renamed, modified, inode metadata) for the
 * whole tree rooted at `path` via a single kernel stream.
 *
 * On other platforms (or when the optional `fsevents` module is missing)
 * it falls back to `fs.watch` so the tool can still run during development.
 *
 * @param {string} path Directory to watch.
 * @param {(event: {event: string, path: string, type: string, changes: object, flags: number}) => void} onChange
 * @returns {() => void} Function that stops the watcher.
 */
export function watch(path, onChange) {
  if (!fsevents) {
    process.emitWarning(
      'Native fsevents module not available; falling back to fs.watch. ' +
        'Install on macOS for low-level FSEvents notifications.',
      'FseventsUnavailable'
    );
    const recursive = process.platform === 'darwin' || process.platform === 'win32';
    const watcher = watchFallback(path, { recursive }, (eventType, filename) => {
      onChange({
        event: eventType === 'rename' ? 'created' : 'modified',
        path: filename ? `${path}/${filename}` : path,
        type: 'file',
        changes: {},
        flags: 0,
      });
    });
    return () => watcher.close();
  }

  return fsevents.watch(path, (changedPath, flags) => {
    const info = fsevents.getInfo(changedPath, flags);
    onChange({ ...info, flags });
  });
}

/**
 * Directory-level FSEvents stream details, useful for diagnostics.
 * @returns {object|null}
 */
export function streamInfo() {
  return fsevents ? fsevents.getInfo.bind(fsevents) : null;
}
