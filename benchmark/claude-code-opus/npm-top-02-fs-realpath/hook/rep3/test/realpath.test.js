import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { resolveRealPath, resolveRealPathSync } from '../src/realpath.js';

let root;
before(() => {
  // tmpdir itself may be a symlink (e.g. /tmp -> /private/tmp on macOS).
  root = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'rp-')));
  fs.mkdirSync(path.join(root, 'real/sub'), { recursive: true });
  fs.writeFileSync(path.join(root, 'real/sub/file.txt'), 'x');
  fs.symlinkSync(path.join(root, 'real'), path.join(root, 'link-abs'), 'dir');
  fs.symlinkSync('real/sub', path.join(root, 'link-rel'), 'dir');
  fs.symlinkSync('link-rel/file.txt', path.join(root, 'chain'));
  fs.symlinkSync('loop-b', path.join(root, 'loop-a'));
  fs.symlinkSync('loop-a', path.join(root, 'loop-b'));
});
after(() => fs.rmSync(root, { recursive: true, force: true }));

const expected = () => path.join(root, 'real/sub/file.txt');

for (const [name, fn] of [['async', resolveRealPath], ['sync', resolveRealPathSync]]) {
  test(`${name}: resolves absolute directory symlink`, async () => {
    assert.equal(await fn(path.join(root, 'link-abs/sub/file.txt')), expected());
  });

  test(`${name}: resolves relative symlink chain`, async () => {
    assert.equal(await fn(path.join(root, 'chain')), expected());
  });

  test(`${name}: resolves relative input against cwd and normalizes ..`, async () => {
    assert.equal(await fn('link-abs/sub/../sub/file.txt', { cwd: root }), expected());
  });

  test(`${name}: throws ENOENT for missing path`, async () => {
    await assert.rejects(async () => fn(path.join(root, 'nope')), { code: 'ENOENT' });
  });

  test(`${name}: throws ELOOP for symlink cycle`, async () => {
    await assert.rejects(async () => fn(path.join(root, 'loop-a')), { code: 'ELOOP' });
  });
}
