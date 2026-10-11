let cached;

export async function loadFsevents() {
  if (cached !== undefined) return cached;

  if (process.platform !== "darwin") {
    cached = null;
    return cached;
  }

  try {
    cached = (await import("fsevents")).default;
  } catch {
    cached = null;
  }

  return cached;
}
