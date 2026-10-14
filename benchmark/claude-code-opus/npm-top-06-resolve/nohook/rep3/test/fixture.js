import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

export const symlink = (target) => ({ symlink: target });

/**
 * Materialises a { 'rel/path': content } tree in a fresh temp directory.
 * Objects are written as JSON, `symlink(target)` creates a symlink.
 * Returns the realpath of the root so results compare cleanly.
 */
export function createFixture(tree) {
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'resolver-')));
  for (const [rel, content] of Object.entries(tree)) {
    const file = path.join(root, rel);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    if (content && typeof content === 'object' && 'symlink' in content) {
      fs.symlinkSync(content.symlink, file);
    } else if (rel.endsWith('/')) {
      fs.mkdirSync(file, { recursive: true });
    } else {
      fs.writeFileSync(file, typeof content === 'string' ? content : JSON.stringify(content));
    }
  }
  return {
    root,
    path: (...parts) => path.join(root, ...parts),
    cleanup: () => fs.rmSync(root, { recursive: true, force: true }),
  };
}
