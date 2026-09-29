import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

let fsevents;
try {
  fsevents = require('fsevents');
} catch (cause) {
  throw new Error(
    'The "fsevents" native module is unavailable. It is a macOS-only addon ' +
      '(FSEvents API) installed as an optional dependency, so it is absent on ' +
      'Linux, Windows, and most CI containers.',
    { cause },
  );
}

export const EVENT_TYPES = Object.freeze([
  'created',
  'cloned',
  'modified',
  'deleted',
  'moved',
  'root-changed',
  'unknown',
]);

export const ITEM_TYPES = Object.freeze(['file', 'directory', 'symlink']);

// Keep every live stop handle referenced. The fsevents README warns that if the
// returned closer is garbage-collected the native watcher is unregistered and
// callbacks silently stop firing.
const liveStreams = new Set();

/**
 * Start a low-level FSEvents stream for a directory tree.
 *
 * @param {string} path Directory (or file) to observe.
 * @param {(event: object) => void} onChange Called with each decoded event:
 *   `{ path, event, type, changes, flags, id }`.
 * @param {object} [options]
 * @param {number} [options.since] Replay events since this event id
 *   (`fsevents.constants` / the `id` from a previous event). Defaults to "now".
 * @returns {() => Promise<void>} Stops the stream.
 */
export function watchNative(path, onChange, options = {}) {
  if (typeof onChange !== 'function') {
    throw new TypeError('watchNative(path, onChange[, { since }]) requires a callback');
  }

  const handler = (changedPath, flags, id) => {
    const info = fsevents.getInfo(changedPath, flags);
    onChange({ ...info, id });
  };

  const rawStop =
    options.since === undefined
      ? fsevents.watch(path, handler)
      : fsevents.watch(path, options.since, handler);

  liveStreams.add(rawStop);

  return async () => {
    liveStreams.delete(rawStop);
    return rawStop();
  };
}

export { fsevents as native };
export const { getInfo, constants } = fsevents;
