'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const test = require('node:test');

const { canonicalPathSync, canonicalPath } = require('../src');

function makeFixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'canonical-path-'));
  const realDir = path.join(root, 'real');
  const realFile = path.join(realDir, 'file.txt');
  fs.mkdirSync(realDir);
  fs.writeFileSync(realFile, 'hello');

  const linkDir = path.join(root, 'link-dir');
  const linkFile = path.join(root, 'link-file.txt');
  fs.symlinkSync(realDir, linkDir);
  fs.symlinkSync(realFile, linkFile);

  return { root, realDir, realFile, linkDir, linkFile };
}

test('resolves a symlinked file to its real path', () => {
  const { root, realFile, linkFile } = makeFixture();
  try {
    assert.strictEqual(canonicalPathSync(linkFile), fs.realpathSync(realFile));
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('resolves through symlinked intermediate directories', () => {
  const { root, realFile, linkDir } = makeFixture();
  try {
    assert.strictEqual(
      canonicalPathSync(path.join(linkDir, 'file.txt')),
      fs.realpathSync(realFile)
    );
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('resolves relative input against the current working directory', () => {
  const { root, realFile } = makeFixture();
  const cwd = process.cwd();
  try {
    process.chdir(root);
    assert.strictEqual(canonicalPathSync('real/file.txt'), fs.realpathSync(realFile));
  } finally {
    process.chdir(cwd);
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('promise variant matches the sync variant', async () => {
  const { root, linkFile } = makeFixture();
  try {
    assert.strictEqual(await canonicalPath(linkFile), canonicalPathSync(linkFile));
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('rejects invalid input', () => {
  assert.throws(() => canonicalPathSync(''), TypeError);
  assert.throws(() => canonicalPathSync(null), TypeError);
  return assert.rejects(() => canonicalPath(''), TypeError);
});
