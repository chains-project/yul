import { FSEventsWatcher } from "./fsevents-watcher.js";
import { FallbackWatcher } from "./fallback-watcher.js";
import { loadFsevents } from "./load-fsevents.js";

export async function watch(paths, options = {}) {
  const native = await loadFsevents();

  if (native) {
    return new FSEventsWatcher(paths, options).start();
  }

  if (options.native === true) {
    throw new Error("native fsevents backend is unavailable on this platform");
  }

  return new FallbackWatcher(paths, options).start();
}

export { FSEventsWatcher, FallbackWatcher, loadFsevents };
