import fs from "node:fs";

const realpathSync = fs.realpathSync;

const nativeRealpath =
  typeof realpathSync.native === "function" ? realpathSync.native : null;

export function resolveRealPath(inputPath) {
  if (typeof inputPath !== "string" || inputPath.length === 0) {
    throw new TypeError("resolveRealPath expects a non-empty string path");
  }

  if (nativeRealpath) {
    try {
      return nativeRealpath(inputPath);
    } catch (err) {
      if (!isFallbackWorthy(err)) {
        throw err;
      }
    }
  }

  return realpathSync(inputPath);
}

function isFallbackWorthy(err) {
  return err && (err.code === "ENOENT" || err.code === "EINVAL");
}

export default resolveRealPath;
