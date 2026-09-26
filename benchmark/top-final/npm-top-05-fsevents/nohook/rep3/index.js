'use strict';

/**
 * Watch a macOS path for native filesystem change notifications.
 * @param {string} path - Absolute path to watch.
 * @param {(path: string, flags: number, info: object) => void} onEvent
 * @returns {() => Promise<void>} stop function
 */
function watch(path, onEvent) {
  if (process.platform !== 'darwin') {
    throw new Error('fsevents watching is only supported on macOS');
  }
  const fsevents = require('fsevents');
  return fsevents.watch(path, onEvent);
}

module.exports = { watch };
