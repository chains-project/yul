import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

/**
 * Load the native FSEvents binding. Throws a descriptive error on
 * non-macOS platforms or when the optional dependency failed to install.
 */
export function loadFsevents() {
  if (process.platform !== 'darwin') {
    throw new Error(`FSEvents is only available on macOS (current platform: ${process.platform})`);
  }
  try {
    return require('fsevents');
  } catch (err) {
    throw new Error(`Failed to load the native fsevents module: ${err.message}`);
  }
}

/**
 * Watch a directory tree for filesystem changes via FSEvents.
 *
 * @param {string} path - Directory to watch (recursively).
 * @param {(event: object) => void} onEvent - Called with fsevents' decoded info:
 *   { path, event, type, changes: { inode, finder, access, xattrs }, flags, id }
 * @returns {() => Promise<void>} Stops the watcher.
 */
export function watch(path, onEvent) {
  const fsevents = loadFsevents();
  return fsevents.watch(path, (changedPath, flags, id) => {
    const info = fsevents.getInfo(changedPath, flags);
    onEvent({ ...info, id });
  });
}
