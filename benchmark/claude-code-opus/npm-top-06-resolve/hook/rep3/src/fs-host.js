import fs from 'node:fs';

/**
 * The resolver never touches `node:fs` directly; it goes through a host so
 * build tools can plug in virtual, cached, or watched filesystems.
 *
 * Like Node's internal `internalModuleStat`, anything that exists and is not
 * a directory is reported as a file.
 */
export const nodeFsHost = {
  stat(p) {
    try {
      const st = fs.statSync(p, { throwIfNoEntry: false });
      if (!st) return undefined;
      return st.isDirectory() ? 'directory' : 'file';
    } catch {
      // ENOTDIR (e.g. "file.js/x"), EACCES, ELOOP: treat as missing, as Node does.
      return undefined;
    }
  },

  readFile(p) {
    try {
      return fs.readFileSync(p, 'utf8');
    } catch (err) {
      if (err.code === 'ENOENT' || err.code === 'ENOTDIR' || err.code === 'EISDIR') return undefined;
      throw err;
    }
  },

  realpath(p) {
    return fs.realpathSync(p);
  },
};
