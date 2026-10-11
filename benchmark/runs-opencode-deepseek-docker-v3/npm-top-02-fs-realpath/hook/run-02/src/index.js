import { promises as fs, realpathSync } from 'fs';

export async function resolveRealPath(input, options) {
  if (typeof input !== 'string') {
    throw new TypeError('Expected a string path');
  }
  return fs.realpath(input, options);
}

export function resolveRealPathSync(input, options) {
  if (typeof input !== 'string') {
    throw new TypeError('Expected a string path');
  }
  return realpathSync(input, options);
}

export default resolveRealPath;
