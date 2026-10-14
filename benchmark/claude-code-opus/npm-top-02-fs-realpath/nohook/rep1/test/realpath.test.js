import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { resolveRealPath, resolveRealPathSync } from '../src/realpath.js';

let root;

before(() => {
  // The tmpdir itself may be a symlink (e.g. /tmp -> /private/tmp on macOS),
  // so canonicalize it first.
  root = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'rp-')));
  fs.mkdirSync(path.join(root, 'real', 'nested'), { recursive: true });
  fs.writeFileSync(path.join(root, 'real', 'nested', 'file.txt'), 'x');
  fs.symlinkSync(path.join(root, 'real'), path.join(root, 'link-dir'), 'dir');
  fs.symlinkSync('link-dir', path.join(root, 'link-to-link'), 'dir');
  fs.symlinkSync(path.join(root, 'missing'), path.join(root, 'dangling'));
});

after(() => fs.rmSync(root, { recursive: true, force: true }));

const expected = () => path.join(root, 'real', 'nested', 'file.txt');

test('resolves a directory symlink in the middle of a path', async () => {
  const p = path.join(root, 'link-dir', 'nested', 'file.txt');
  assert.equal(await resolveRealPath(p), expected());
  assert.equal(resolveRealPathSync(p), expected());
});

test('resolves chained relative symlinks', async () => {
  const p = path.join(root, 'link-to-link', 'nested', 'file.txt');
  assert.equal(await resolveRealPath(p), expected());
});

test('normalizes . and .. segments', async () => {
  const p = path.join(root, 'link-dir', 'nested', '..', 'nested', '.', 'file.txt');
  assert.equal(await resolveRealPath(p), expected());
});

test('resolves relative paths against cwd', async () => {
  const cwd = process.cwd();
  process.chdir(root);
  try {
    assert.equal(await resolveRealPath('link-dir/nested/file.txt'), expected());
  } finally {
    process.chdir(cwd);
  }
});

test('rejects with ENOENT for dangling symlinks and missing paths', async () => {
  await assert.rejects(resolveRealPath(path.join(root, 'dangling')), { code: 'ENOENT' });
  assert.throws(() => resolveRealPathSync(path.join(root, 'nope')), { code: 'ENOENT' });
});
