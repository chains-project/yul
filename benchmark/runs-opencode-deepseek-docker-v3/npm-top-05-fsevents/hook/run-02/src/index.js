import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

const fsevents = loadFsevents();

function loadFsevents() {
  if (process.platform !== 'darwin') return null;
  try {
    return require('fsevents');
  } catch {
    return null;
  }
}

export const native = fsevents !== null;

export const Event = Object.freeze({
  CREATED: 'created',
  MODIFIED: 'modified',
  DELETED: 'deleted',
  RENAMED: 'renamed',
  ROOT_CHANGED: 'root-changed',
  UNKNOWN: 'unknown',
});

export function watch(path, onEvent, options = {}) {
  if (!fsevents) {
    throw new Error(
      process.platform === 'darwin'
        ? 'The native "fsevents" addon is not built. Run: npm rebuild fsevents'
        : 'The "fsevents" addon is only available on macOS.',
    );
  }

  const { id = 0, latency, flags = {} } = options;

  const stop = fsevents.watch(
    path,
    (changedPath, eventFlags, eventId) => {
      const info = fsevents.getInfo(changedPath, eventFlags, eventId);
      onEvent({
        path: info.path,
        event: normalizeEvent(info.event),
        type: info.type,
        changes: info.changes,
        flags: info.flags,
        id: info.id,
        raw: info,
      });
    },
    { latency, flags, id },
  );

  return stop;
}

export async function* stream(path, options = {}) {
  const queue = [];
  let resolve;
  let done = false;

  const stop = watch(
    path,
    (event) => {
      queue.push(event);
      if (resolve) {
        resolve();
        resolve = undefined;
      }
    },
    options,
  );

  try {
    while (!done) {
      if (queue.length === 0) {
        await new Promise((r) => {
          resolve = r;
        });
      }
      while (queue.length > 0) yield queue.shift();
    }
  } finally {
    done = true;
    stop();
  }
}

function normalizeEvent(event) {
  switch (event) {
    case 'created':
    case 'modified':
    case 'deleted':
    case 'renamed':
    case 'root-changed':
      return event;
    default:
      return Event.UNKNOWN;
  }
}
