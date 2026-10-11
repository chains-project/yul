import { EventEmitter } from 'node:events';
import { watch } from 'node:fs';

export class PortableBackend extends EventEmitter {
  #watcher = null;

  constructor(path, options = {}) {
    super();
    this.name = 'fs.watch';
    this.path = path;
    this.options = options;
  }

  start() {
    const { persistent = true, recursive = true } = this.options;

    this.#watcher = watch(this.path, { persistent, recursive }, (eventType, filename) => {
      this.emit('change', {
        path: filename ? `${this.path}/${filename}` : this.path,
        id: null,
        type: eventType === 'rename' ? 'renamed' : 'modified',
        flags: 0,
      });
    });

    return this;
  }

  stop() {
    this.#watcher?.close();
    this.#watcher = null;
  }
}
