import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { realpath, realpathSync } from '../src/realpath.js';

let root;

before(() => {
  // tmpdir itself may be a symlink (e.g. /tmp -> /private/tmp on macOS).
  root = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'canon-')));
  fs.mkdirSync(path.join(root, 'real', 'nested'), { recursive: true });
  fs.writeFileSync(path.join(root, 'real', 'nested', 'file.txt'), 'hi');
  fs.symlinkSync(path.join(root, 'real'), path.join(root, 'link-abs'));
  fs.symlinkSync('real/nested', path.join(root, 'link-rel'));
  fs.symlinkSync('link-abs', path.join(root, 'link-chain'));
  fs.symlinkSync('loop-b', path.join(root, 'loop-a'));
  fs.symlinkSync('loop-a', path.join(root, 'loop-b'));
});

after(() => fs.rmSync(root, { recursive: true, force: true }));

const expected = () => path.join(root, 'real', 'nested', 'file.txt');

for (const [name, fn] of [['async', realpath], ['sync', realpathSync]]) {
  test(`${name}: absolute symlink`, async () => {
    assert.equal(await fn(path.join(root, 'link-abs', 'nested', 'file.txt')), expected());
  });

  test(`${name}: relative symlink target`, async () => {
    assert.equal(await fn(path.join(root, 'link-rel', 'file.txt')), expected());
  });

  test(`${name}: chained symlinks and .. segments`, async () => {
    assert.equal(
      await fn(path.join(root, 'link-chain', 'nested', '..', 'nested', 'file.txt')),
      expected(),
    );
  });

  test(`${name}: relative input resolves against cwd`, async () => {
    const cwd = process.cwd();
    process.chdir(root);
    try {
      assert.equal(await fn('link-rel/file.txt'), expected());
    } finally {
      process.chdir(cwd);
    }
  });

  test(`${name}: missing path throws ENOENT`, async () => {
    await assert.rejects(async () => fn(path.join(root, 'nope')), { code: 'ENOENT' });
  });

  test(`${name}: symlink loop throws ELOOP`, async () => {
    await assert.rejects(async () => fn(path.join(root, 'loop-a')), { code: 'ELOOP' });
  });
}

test('sync and async agree', async () => {
  const p = path.join(root, 'link-chain', 'nested');
  assert.equal(await realpath(p), realpathSync(p));
});
