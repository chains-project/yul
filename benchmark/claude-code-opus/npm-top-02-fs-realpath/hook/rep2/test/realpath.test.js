import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { canonicalPath, canonicalPathSync } from '../src/realpath.js';

let root; // canonical temp dir (os.tmpdir() may itself be a symlink, e.g. macOS)
let realFile;

before(() => {
  root = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'canon-')));
  fs.mkdirSync(path.join(root, 'real', 'nested'), { recursive: true });
  realFile = path.join(root, 'real', 'nested', 'file.txt');
  fs.writeFileSync(realFile, 'x');
  fs.symlinkSync(path.join(root, 'real'), path.join(root, 'dirlink'), 'dir');
  fs.symlinkSync(realFile, path.join(root, 'filelink'));
  // A relative symlink pointing to another symlink.
  fs.symlinkSync('filelink', path.join(root, 'chain'));
  fs.symlinkSync('loop-b', path.join(root, 'loop-a'));
  fs.symlinkSync('loop-a', path.join(root, 'loop-b'));
});

after(() => fs.rmSync(root, { recursive: true, force: true }));

for (const [name, resolve] of [
  ['async', canonicalPath],
  ['sync', async (p) => canonicalPathSync(p)],
]) {
  test(`${name}: resolves a directory symlink in the middle of a path`, async () => {
    assert.equal(await resolve(path.join(root, 'dirlink', 'nested', 'file.txt')), realFile);
  });

  test(`${name}: resolves a file symlink and a chain of relative links`, async () => {
    assert.equal(await resolve(path.join(root, 'filelink')), realFile);
    assert.equal(await resolve(path.join(root, 'chain')), realFile);
  });

  test(`${name}: normalizes . and .. after resolving links`, async () => {
    const p = path.join(root, 'dirlink', 'nested', '..', 'nested', '.', 'file.txt');
    assert.equal(await resolve(p), realFile);
  });

  test(`${name}: resolves relative paths against cwd`, async () => {
    const cwd = process.cwd();
    process.chdir(path.join(root, 'dirlink'));
    try {
      assert.equal(await resolve('nested/file.txt'), realFile);
    } finally {
      process.chdir(cwd);
    }
  });

  test(`${name}: accepts file: URLs and Buffers`, async () => {
    assert.equal(await resolve(pathToFileURL(path.join(root, 'filelink'))), realFile);
    assert.equal(await resolve(Buffer.from(path.join(root, 'filelink'))), realFile);
  });

  test(`${name}: rejects missing paths with ENOENT`, async () => {
    await assert.rejects(resolve(path.join(root, 'nope')), { code: 'ENOENT' });
  });

  test(`${name}: rejects symlink loops with ELOOP`, async () => {
    await assert.rejects(resolve(path.join(root, 'loop-a')), { code: 'ELOOP' });
  });

  test(`${name}: rejects invalid input`, async () => {
    await assert.rejects(resolve(''), TypeError);
    await assert.rejects(resolve(42), TypeError);
  });
}
