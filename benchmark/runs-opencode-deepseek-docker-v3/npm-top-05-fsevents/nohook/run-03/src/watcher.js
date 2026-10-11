import { EventEmitter } from 'node:events';
import path from 'node:path';
import fs from 'node:fs';

let fsevents = null;
if (process.platform === 'darwin') {
  try {
    ({ default: fsevents } = await import('fsevents'));
  } catch {
    fsevents = null;
  }
}

export const usingNativeFSEvents = fsevents !== null;

export function watch(root, options = {}) {
  const emitter = new EventEmitter();

  if (fsevents) {
    const stop = fsevents.watch(root, (eventPath, flags, id) => {
      const info = fsevents.getInfo(eventPath, flags, id);
      emitter.emit('all', info);
      emitter.emit(info.event, info);
    });

    emitter.close = () => stop();
    return emitter;
  }

  const watcher = fs.watch(root, { recursive: true }, (eventType, filename) => {
    const info = {
      event: eventType === 'rename' ? 'rename' : 'change',
      path: filename ? path.join(root, filename) : root,
    };
    emitter.emit('all', info);
    emitter.emit(info.event, info);
  });

  emitter.close = () => watcher.close();
  return emitter;
}
