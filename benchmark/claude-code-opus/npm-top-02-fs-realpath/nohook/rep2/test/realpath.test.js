import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { resolveRealPath, resolveRealPathSync } from '../src/realpath.js';

let root;

before(() => {
  // tmpdir itself may be a symlink (e.g. /tmp -> /private/tmp on macOS).
  root = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'realpath-')));
  fs.mkdirSync(path.join(root, 'real/nested'), { recursive: true });
  fs.writeFileSync(path.join(root, 'real/nested/file.txt'), 'x');
  fs.symlinkSync(path.join(root, 'real'), path.join(root, 'dirlink'), 'dir');
  fs.symlinkSync('dirlink/nested/file.txt', path.join(root, 'filelink'));
  fs.symlinkSync('filelink', path.join(root, 'chain'));
  fs.symlinkSync('loop-b', path.join(root, 'loop-a'));
  fs.symlinkSync('loop-a', path.join(root, 'loop-b'));
  fs.symlinkSync('missing', path.join(root, 'dangling'));
});

after(() => fs.rmSync(root, { recursive: true, force: true }));

const expected = () => path.join(root, 'real/nested/file.txt');

for (const [name, fn] of [['async', resolveRealPath], ['sync', resolveRealPathSync]]) {
  test(`${name}: resolves a symlinked directory component`, async () => {
    assert.equal(await fn(path.join(root, 'dirlink/nested/file.txt')), expected());
  });

  test(`${name}: resolves a chain of relative file symlinks`, async () => {
    assert.equal(await fn(path.join(root, 'chain')), expected());
  });

  test(`${name}: resolves relative input against cwd and normalizes ..`, async () => {
    assert.equal(await fn('dirlink/nested/../nested/file.txt', { cwd: root }), expected());
  });

  test(`${name}: rejects dangling symlinks with ENOENT`, async () => {
    await assert.rejects(async () => fn(path.join(root, 'dangling')), { code: 'ENOENT' });
  });

  test(`${name}: rejects symlink loops with ELOOP`, async () => {
    await assert.rejects(async () => fn(path.join(root, 'loop-a')), { code: 'ELOOP' });
  });

  test(`${name}: rejects empty input`, async () => {
    await assert.rejects(async () => fn(''), TypeError);
  });
}
