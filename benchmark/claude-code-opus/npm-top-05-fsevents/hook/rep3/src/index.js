import { EventEmitter } from 'node:events';
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(import.meta.url);

let fsevents;
function loadFsevents() {
  if (fsevents) return fsevents;
  if (process.platform !== 'darwin') {
    throw new Error(`FSEvents is only available on macOS (current platform: ${process.platform})`);
  }
  fsevents = require('fsevents');
  return fsevents;
}

/**
 * Watches a directory tree using native macOS FSEvents.
 *
 * Emits 'change' ({ path, event, type, flags, id, changes }) for every filesystem event.
 */
export class Watcher extends EventEmitter {
  #root;
  #since;
  #stop = null;

  /**
   * @param {string} root      Directory to watch (recursively).
   * @param {object} [options]
   * @param {number} [options.since]  FSEvents event ID to replay history from.
   */
  constructor(root, { since } = {}) {
    super();
    this.#root = path.resolve(root);
    this.#since = since;
  }

  get root() {
    return this.#root;
  }

  get running() {
    return this.#stop !== null;
  }

  start() {
    if (this.#stop) return this;
    const fse = loadFsevents();
    const handler = (file, flags, id) => {
      const info = fse.getInfo(file, flags);
      this.emit('change', { ...info, flags, id });
    };
    this.#stop = this.#since === undefined
      ? fse.watch(this.#root, handler)
      : fse.watch(this.#root, this.#since, handler);
    return this;
  }

  async stop() {
    if (!this.#stop) return;
    const stop = this.#stop;
    this.#stop = null;
    await stop();
  }
}

export function watch(root, onChange, options) {
  const watcher = new Watcher(root, options);
  if (onChange) watcher.on('change', onChange);
  return watcher.start();
}
