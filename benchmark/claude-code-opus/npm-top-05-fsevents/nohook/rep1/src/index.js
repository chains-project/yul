'use strict';

let fsevents;
try {
  fsevents = require('fsevents');
} catch (err) {
  fsevents = null;
}

function isSupported() {
  return process.platform === 'darwin' && fsevents !== null;
}

/**
 * Watch a path using macOS FSEvents.
 * @param {string} path - Directory (or file) to watch.
 * @param {(event: object) => void} onEvent - Called with
 *   { path, flags, id, type, event, changes } for each change.
 * @returns {() => Promise<void>} stop function
 */
function watch(path, onEvent) {
  if (!isSupported()) {
    throw new Error('fsevents is unavailable: this tool requires macOS');
  }
  return fsevents.watch(path, (eventPath, flags, id) => {
    const info = fsevents.getInfo(eventPath, flags);
    onEvent({ ...info, id });
  });
}

module.exports = { watch, isSupported };
