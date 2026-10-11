import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  mkdtempSync,
  mkdirSync,
  realpathSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { canonicalPath } from '../index.js';

function withTempDir(fn) {
  const dir = mkdtempSync(join(tmpdir(), 'canonical-path-'));
  const base = realpathSync(dir);
  try {
    return fn(base);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

test('returns the real path for a regular file', () => {
  withTempDir((base) => {
    const file = join(base, 'real.txt');
    writeFileSync(file, 'hello');
    assert.equal(canonicalPath(file), file);
  });
});

test('resolves a symlink to its target', () => {
  withTempDir((base) => {
    const target = join(base, 'target.txt');
    writeFileSync(target, 'hello');
    const link = join(base, 'link.txt');
    symlinkSync(target, link);
    assert.equal(canonicalPath(link), target);
  });
});

test('resolves symlinked directories and chained links', () => {
  withTempDir((base) => {
    const nested = join(base, 'a', 'b');
    mkdirSync(nested, { recursive: true });
    const file = join(nested, 'file.txt');
    writeFileSync(file, 'hello');
    const link1 = join(base, 'link1');
    const link2 = join(base, 'link2');
    symlinkSync(nested, link1);
    symlinkSync(link1, link2, 'dir');
    assert.equal(canonicalPath(link2), nested);
    assert.equal(canonicalPath(join(link2, 'file.txt')), file);
  });
});

test('throws ENOENT for a missing path', () => {
  withTempDir((base) => {
    assert.throws(() => canonicalPath(join(base, 'nope.txt')), {
      code: 'ENOENT',
    });
  });
});
