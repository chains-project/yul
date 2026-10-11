import { EventEmitter } from "node:events";
import { loadFsevents } from "./load-fsevents.js";

export class FSEventsWatcher extends EventEmitter {
  constructor(paths, options = {}) {
    super();
    this.paths = Array.isArray(paths) ? paths : [paths];
    this.options = options;
    this.stops = [];
    this.closed = false;
    this.fsevents = null;
  }

  async start() {
    const fsevents = await loadFsevents();
    if (!fsevents) {
      throw new Error("native fsevents module is not available");
    }

    this.fsevents = fsevents;

    for (const target of this.paths) {
      const stop = fsevents.watch(
        target,
        (path, flags, id) => this.#onEvent(path, flags, id),
        {
          latency: this.options.latency ?? 0.25,
          since: this.options.since ?? undefined,
          flags: this.options.flags,
        },
      );
      this.stops.push(stop);
    }

    this.emit("ready");
    return this;
  }

  #onEvent(path, flags, id) {
    const info = this.fsevents.getInfo(path, flags);
    const event = {
      path,
      id,
      event: info.event,
      type: info.type,
      changes: info.changes,
      flags,
    };

    this.emit("event", event);
    this.emit(info.event, event);
  }

  close() {
    if (this.closed) return;
    this.closed = true;

    for (const stop of this.stops) {
      try {
        stop();
      } catch {}
    }

    this.stops = [];
    this.emit("close");
  }
}
