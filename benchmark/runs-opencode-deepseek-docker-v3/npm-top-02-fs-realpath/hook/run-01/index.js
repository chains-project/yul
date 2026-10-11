import { realpathSync } from 'node:fs';

export function canonicalPath(inputPath) {
  return realpathSync(inputPath);
}

export default canonicalPath;
