import { EventEmitter } from "node:events";
import fs from "node:fs";
import path from "node:path";

export class FallbackWatcher extends EventEmitter {
  constructor(paths, options = {}) {
    super();
    this.paths = Array.isArray(paths) ? paths : [paths];
    this.options = options;
    this.watchers = [];
    this.closed = false;
  }

  async start() {
    for (const target of this.paths) {
      let stat;
      try {
        stat = fs.statSync(target);
      } catch (err) {
        this.emit("error", err);
        continue;
      }

      const recursive = stat.isDirectory() && this.options.recursive !== false;
      let watcher;
      try {
        watcher = fs.watch(target, { recursive, persistent: true }, (eventType, filename) => {
          const full = filename ? path.join(target, filename.toString()) : target;
          const event = eventType === "rename" ? "renamed" : "modified";
          const info = { path: full, id: -1, event, type: "unknown", changes: {}, flags: 0 };
          this.emit("event", info);
          this.emit(event, info);
        });
      } catch (err) {
        this.emit("error", err);
        continue;
      }

      watcher.on("error", (err) => this.emit("error", err));
      this.watchers.push(watcher);
    }

    this.emit("ready");
    return this;
  }

  close() {
    if (this.closed) return;
    this.closed = true;

    for (const watcher of this.watchers) {
      try {
        watcher.close();
      } catch {}
    }

    this.watchers = [];
    this.emit("close");
  }
}
