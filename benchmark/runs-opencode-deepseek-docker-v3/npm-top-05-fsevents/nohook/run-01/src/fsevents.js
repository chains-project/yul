import { EventEmitter } from 'node:events';

export class FSEventsBackend extends EventEmitter {
  #stream = null;

  constructor(fsevents, path, options = {}) {
    super();
    this.name = 'fsevents';
    this.fsevents = fsevents;
    this.path = path;
    this.options = options;
  }

  start() {
    const { constants } = this.fsevents;

    this.#stream = this.fsevents.watch(
      this.path,
      (changedPath, flags, id) => {
        this.emit('change', {
          path: changedPath,
          id,
          type: classify(flags, constants),
          flags,
        });
      },
      { persistent: true, ...this.options },
    );

    return this;
  }

  stop() {
    this.#stream?.stop();
    this.#stream = null;
  }
}

function classify(flags, c) {
  if (flags & c.ItemRemoved) return 'deleted';
  if (flags & c.ItemCreated) return 'created';
  if (flags & c.ItemRenamed) return 'renamed';
  if (flags & c.MustScanSubDirs || flags & c.RootChanged) return 'rescan';
  if (
    flags & c.ItemModified ||
    flags & c.ItemInodeMetaMod ||
    flags & c.ItemChangeOwner ||
    flags & c.ItemXattrMod
  ) {
    return 'modified';
  }
  return 'unknown';
}
