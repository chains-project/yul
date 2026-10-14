import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

export const symlink = (target) => ({ [SYMLINK]: target });
const SYMLINK = Symbol('symlink');

/**
 * Write a fixture tree into a fresh temp directory and return its real path.
 * Keys are relative paths; values are file contents (strings or JSON-able
 * objects for *.json), nested trees, or `symlink(target)`.
 */
export function createFixture(tree) {
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'node-resolver-')));
  writeTree(root, tree);
  return root;
}

export function removeFixture(root) {
  fs.rmSync(root, { recursive: true, force: true });
}

function writeTree(dir, tree) {
  for (const [name, value] of Object.entries(tree)) {
    const target = path.join(dir, name);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    if (typeof value === 'string') {
      fs.writeFileSync(target, value);
    } else if (value[SYMLINK]) {
      fs.symlinkSync(value[SYMLINK], target);
    } else if (name.endsWith('.json')) {
      fs.writeFileSync(target, JSON.stringify(value, null, 2));
    } else {
      fs.mkdirSync(target, { recursive: true });
      writeTree(target, value);
    }
  }
}

/** Run a resolver and normalize the outcome to { path } or { code }. */
export function outcome(fn) {
  try {
    return { path: fn() };
  } catch (err) {
    if (!err.code) throw err;
    return { code: err.code };
  }
}
