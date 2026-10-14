import { createRequire } from 'node:module';
import { EventEmitter } from 'node:events';
import path from 'node:path';

const require = createRequire(import.meta.url);

/**
 * Load the native FSEvents binding. It only builds/installs on macOS,
 * so it is an optional dependency and loaded lazily.
 */
export function loadFsevents() {
  if (process.platform !== 'darwin') {
    throw new Error(`FSEvents is only available on macOS (current platform: ${process.platform})`);
  }
  try {
    return require('fsevents');
  } catch (err) {
    throw new Error(`Failed to load the native "fsevents" module. Try reinstalling dependencies.\n${err.message}`);
  }
}

/**
 * Translate raw FSEvents flags into a simple event description.
 */
export function describe(fsevents, filePath, flags, id) {
  const info = fsevents.getInfo(filePath, flags, id);
  return {
    path: info.path,
    event: info.event, // created | modified | deleted | moved | root-changed | cloned | unknown
    type: info.type, // file | directory | symlink
    changes: info.changes, // { inode, finder, access, xattrs }
    flags,
    id,
  };
}

/**
 * Watch a directory tree using FSEvents.
 * Emits 'change' with a described event object. Call .close() to stop.
 */
export function watch(target, { since } = {}) {
  const fsevents = loadFsevents();
  const root = path.resolve(target);
  const emitter = new EventEmitter();

  const stop = fsevents.watch(root, since, (filePath, flags, id) => {
    emitter.emit('change', describe(fsevents, filePath, flags, id));
  });

  emitter.close = () => stop();
  return emitter;
}
