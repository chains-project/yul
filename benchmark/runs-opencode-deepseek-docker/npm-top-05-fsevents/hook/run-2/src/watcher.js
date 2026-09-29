import { EventEmitter } from 'node:events';
import fs from 'node:fs';
import { join } from 'node:path';

/**
 * macOS FSEvents flag names, indexed by bit position. These mirror the flags
 * defined in Apple's <CoreServices/FSEvents.h> as surfaced by the fsevents addon.
 */
export const FLAG_NAMES = [
  'None',
  'MustScanSubDirs',
  'UserDropped',
  'KernelDropped',
  'EventIdsWrapped',
  'HistoryDone',
  'RootChanged',
  'Mount',
  'Unmount',
  'ItemCreated',
  'ItemRemoved',
  'ItemInodeMetaMod',
  'ItemRenamed',
  'ItemModified',
  'ItemFinderInfoMod',
  'ItemChangeOwner',
  'ItemXattrMod',
  'ItemIsFile',
  'ItemIsDir',
  'ItemIsSymlink',
  'OwnEvent',
  'ItemIsHardlink',
  'ItemIsLastHardlink',
  'ItemCloned',
];

/**
 * The native binding only builds on darwin. On other platforms (or if the
 * optional dependency was skipped) we fall back to Node's portable watcher.
 */
let native = null;
try {
  native = (await import('fsevents')).default;
} catch {
  native = null;
}

export function nativeAvailable() {
  return native != null;
}

function bitFlagsToNames(flags) {
  const names = [];
  for (let bit = 0; bit < FLAG_NAMES.length; bit += 1) {
    if (flags & (1 << bit)) names.push(FLAG_NAMES[bit]);
  }
  return names;
}

function nativeWatch(path, { recursive = true, latency, debounce, since, persistent } = {}) {
  const emitter = new EventEmitter();
  const opts = { recursive, persistent };
  if (latency != null) opts.latency = latency;
  if (debounce != null) opts.debounce = debounce;
  if (since != null) opts.since = since;

  const stop = native.watch(
    path,
    (eventPath, flags, id) => {
      const info = native.getInfo(eventPath, flags, id);
      emitter.emit('event', {
        path: eventPath,
        event: info.event,
        type: info.type,
        changes: info.changes,
        flags,
        flagNames: bitFlagsToNames(flags),
        id,
        native: true,
      });
    },
    opts,
  );

  emitter.close = () => stop();
  return emitter;
}

function fallbackWatch(path, { recursive = true, persistent = true } = {}) {
  const emitter = new EventEmitter();
  const onChange = (eventType, filename) => {
    emitter.emit('event', {
      path: filename ? join(path, filename) : path,
      event: eventType === 'rename' ? 'renamed' : 'modified',
      type: null,
      changes: null,
      flags: null,
      flagNames: [],
      id: null,
      native: false,
    });
  };

  // Recursive fs.watch only exists on macOS and Windows; degrade elsewhere.
  let watcher;
  try {
    watcher = fs.watch(path, { recursive, persistent }, onChange);
  } catch (err) {
    if (err.code !== 'ERR_FEATURE_UNAVAILABLE_ON_PLATFORM') throw err;
    watcher = fs.watch(path, { recursive: false, persistent }, onChange);
  }

  emitter.close = () => watcher.close();
  return emitter;
}

/**
 * Watch a path for low-level filesystem changes.
 *
 * On macOS this uses the native FSEvents API, which reports coalesced,
 * per-path change records for entire directory trees. Elsewhere it degrades
 * to `fs.watch`.
 *
 * @returns {EventEmitter & { close(): void }} emits `event` objects
 */
export function watch(path, options = {}) {
  if (native) return nativeWatch(path, options);
  return fallbackWatch(path, options);
}
