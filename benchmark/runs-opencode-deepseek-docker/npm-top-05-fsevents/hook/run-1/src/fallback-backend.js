import { watch } from "node:fs";
import { join } from "node:path";

export function watchWithFallback(root, onEvent) {
  let watcher;
  try {
    watcher = watch(root, { recursive: true }, handler);
  } catch (err) {
    if (err.code !== "ERR_FEATURE_UNAVAILABLE_ON_PLATFORM") throw err;
    watcher = watch(root, handler);
  }

  function handler(eventType, filename) {
    onEvent({
      path: filename ? join(root, filename) : root,
      event: eventType === "rename" ? "unknown" : "modified",
      type: undefined,
      changes: {},
    });
  }

  return {
    backend: "fs.watch",
    close: () => watcher.close(),
  };
}
