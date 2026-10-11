import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, symlink, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { resolveRealPath, resolveRealPathSync } from '../src/index.js';

async function withTempDir(fn) {
  const dir = await mkdtemp(join(tmpdir(), 'realpath-resolver-'));
  try {
    return await fn(dir);
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
}

test('resolves a symlink to its target', async () => {
  await withTempDir(async (dir) => {
    const target = join(dir, 'target.txt');
    const link = join(dir, 'link.txt');
    await writeFile(target, 'hello');
    await symlink(target, link);

    assert.equal(await resolveRealPath(link), await resolveRealPath(target));
  });
});

test('returns the canonical path for a real path', async () => {
  await withTempDir(async (dir) => {
    assert.equal(await resolveRealPath(dir), await resolveRealPath(dir));
  });
});

test('sync and async variants agree', async () => {
  await withTempDir(async (dir) => {
    const target = join(dir, 'target.txt');
    const link = join(dir, 'link.txt');
    await writeFile(target, 'hello');
    await symlink(target, link);

    assert.equal(resolveRealPathSync(link), await resolveRealPath(link));
  });
});

test('rejects non-existent paths', async () => {
  await assert.rejects(resolveRealPath(join(tmpdir(), 'realpath-missing-xyz')));
});

test('rejects non-string input', async () => {
  await assert.rejects(resolveRealPath(null), TypeError);
});
