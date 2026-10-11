import { realpath, realpathSync } from "node:fs";
import { promisify } from "node:util";

const realpathAsync = promisify(realpath);

export function resolveRealPath(inputPath, options) {
  return realpathAsync(inputPath, options);
}

export function resolveRealPathSync(inputPath, options) {
  return realpathSync(inputPath, options);
}

export default resolveRealPath;
