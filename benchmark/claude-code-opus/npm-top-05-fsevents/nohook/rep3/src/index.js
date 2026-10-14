import fsevents from 'fsevents';

/**
 * Watch a directory tree using macOS FSEvents.
 *
 * @param {string} root - Absolute or relative path to watch (recursive).
 * @param {(event: WatchEvent) => void} onEvent - Called for each change.
 * @returns {() => Promise<void>} Stop function; resolves once the stream is closed.
 *
 * @typedef {object} WatchEvent
 * @property {string} path - Absolute path of the changed entry.
 * @property {string} event - created | modified | deleted | moved | root-changed | unknown
 * @property {string} type - file | directory | symlink
 * @property {{inode: boolean, finder: boolean, access: boolean, xattrs: boolean}} changes
 * @property {number} flags - Raw FSEventStreamEventFlags bitmask.
 * @property {number} id - FSEvents event ID (monotonic, usable for resume-from-ID).
 */
export function watch(root, onEvent) {
  return fsevents.watch(root, (path, flags, id) => {
    const info = fsevents.getInfo(path, flags);
    onEvent({ ...info, id });
  });
}

export const constants = fsevents.constants;
