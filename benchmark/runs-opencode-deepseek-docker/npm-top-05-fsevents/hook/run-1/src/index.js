const DARWIN = process.platform === "darwin";

export async function createWatcher(root, onEvent) {
  if (DARWIN) {
    try {
      const { watchWithFsevents } = await import("./fsevents-backend.js");
      return watchWithFsevents(root, onEvent);
    } catch (err) {
      if (err.code !== "ERR_MODULE_NOT_FOUND" && err.code !== "MODULE_NOT_FOUND") {
        throw err;
      }
    }
  }
  const { watchWithFallback } = await import("./fallback-backend.js");
  return watchWithFallback(root, onEvent);
}
