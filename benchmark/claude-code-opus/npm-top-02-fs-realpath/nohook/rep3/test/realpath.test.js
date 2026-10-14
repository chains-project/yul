'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { resolveRealpath, resolveRealpathSync } = require('../src/realpath');

// The tmpdir itself may be a symlink (e.g. /tmp -> /private/tmp on macOS),
// so canonicalize the root before building expectations.
const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'realpath-test-')));
const target = path.join(root, 'real', 'file.txt');
fs.mkdirSync(path.dirname(target));
fs.writeFileSync(target, 'hi');

const canSymlink = (() => {
  try {
    fs.symlinkSync(path.join(root, 'real'), path.join(root, 'dirlink'), 'dir');
    fs.symlinkSync(path.join(root, 'dirlink', 'file.txt'), path.join(root, 'filelink'));
    fs.symlinkSync('filelink', path.join(root, 'chain')); // relative link to a link
    fs.symlinkSync(path.join(root, 'missing'), path.join(root, 'dangling'));
    fs.symlinkSync('loop-b', path.join(root, 'loop-a'));
    fs.symlinkSync('loop-a', path.join(root, 'loop-b'));
    return true;
  } catch {
    return false; // e.g. Windows without symlink privilege
  }
})();

test.after(() => fs.rmSync(root, { recursive: true, force: true }));

for (const [name, fn] of [['async', resolveRealpath], ['sync', resolveRealpathSync]]) {
  const call = async (p) => fn(p);

  test(`${name}: plain path resolves to itself`, async () => {
    assert.strictEqual(await call(target), target);
  });

  test(`${name}: normalizes . and .. segments`, async () => {
    assert.strictEqual(await call(path.join(root, 'real', '.', '..', 'real', 'file.txt')), target);
  });

  test(`${name}: relative paths resolve against cwd`, async () => {
    const cwd = process.cwd();
    process.chdir(root);
    try {
      assert.strictEqual(await call(path.join('real', 'file.txt')), target);
    } finally {
      process.chdir(cwd);
    }
  });

  test(`${name}: symlinked directory component`, { skip: !canSymlink }, async () => {
    assert.strictEqual(await call(path.join(root, 'dirlink', 'file.txt')), target);
  });

  test(`${name}: chain of relative and absolute links`, { skip: !canSymlink }, async () => {
    assert.strictEqual(await call(path.join(root, 'chain')), target);
  });

  test(`${name}: dangling link rejects with ENOENT`, { skip: !canSymlink }, async () => {
    await assert.rejects(call(path.join(root, 'dangling')), { code: 'ENOENT' });
  });

  test(`${name}: symlink loop rejects with ELOOP`, { skip: !canSymlink }, async () => {
    await assert.rejects(call(path.join(root, 'loop-a')), { code: 'ELOOP' });
  });

  test(`${name}: rejects empty and non-string input`, async () => {
    await assert.rejects(call(''), TypeError);
    await assert.rejects(call(42), TypeError);
  });
}
