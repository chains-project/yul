import { createRequire } from 'node:module';
import { watch as fsWatch } from 'node:fs';
import { resolve, join } from 'node:path';
import { EventEmitter } from 'node:events';

const require = createRequire(import.meta.url);

/**
 * Load the native FSEvents binding. It is an optional, darwin-only
 * dependency, so it is absent on other platforms.
 */
function loadFsevents() {
  if (process.platform !== 'darwin') return null;
  try {
    return require('fsevents');
  } catch {
    return null;
  }
}

export const fsevents = loadFsevents();
export const isNative = fsevents !== null;

/**
 * Watch `root` recursively for filesystem changes.
 *
 * Emits:
 *   'change' ({ path, event, type, flags, id })
 *   'error'  (err)
 *
 * On macOS this uses FSEvents directly via the `fsevents` native addon,
 * which exposes raw event flags and event IDs. Elsewhere it falls back to
 * `fs.watch` (useful for development/CI, but with coarser events).
 */
export function watch(root) {
  const emitter = new EventEmitter();
  const absRoot = resolve(root);
  let stop;

  if (fsevents) {
    const stopNative = fsevents.watch(absRoot, (path, flags, id) => {
      const info = fsevents.getInfo(path, flags);
      emitter.emit('change', {
        path,
        event: info.event, // created | modified | deleted | moved | root-changed | unknown
        type: info.type, // file | directory | symlink
        flags,
        id,
      });
    });
    stop = () => stopNative();
  } else {
    const watcher = fsWatch(absRoot, { recursive: true }, (eventType, filename) => {
      emitter.emit('change', {
        path: filename ? join(absRoot, filename.toString()) : absRoot,
        event: eventType === 'rename' ? 'renamed' : 'modified',
        type: 'unknown',
        flags: null,
        id: null,
      });
    });
    watcher.on('error', (err) => emitter.emit('error', err));
    stop = async () => watcher.close();
  }

  emitter.close = async () => {
    await stop();
    emitter.removeAllListeners();
  };
  return emitter;
}
