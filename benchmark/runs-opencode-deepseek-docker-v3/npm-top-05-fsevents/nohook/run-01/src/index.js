import { platform } from 'node:os';

import { FSEventsBackend } from './fsevents.js';
import { PortableBackend } from './portable.js';

export async function watch(path, options = {}) {
  const backend = await createBackend(path, options);
  return backend.start();
}

async function createBackend(path, options) {
  if (platform() === 'darwin') {
    try {
      const { default: fsevents } = await import('fsevents');
      return new FSEventsBackend(fsevents, path, options);
    } catch (error) {
      if (error.code !== 'ERR_MODULE_NOT_FOUND' && error.code !== 'MODULE_NOT_FOUND') {
        throw error;
      }
    }
  }

  return new PortableBackend(path, options);
}
