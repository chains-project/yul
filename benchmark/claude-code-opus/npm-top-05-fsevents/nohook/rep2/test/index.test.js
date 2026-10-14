import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { watch, loadFsevents } from '../src/index.js';

const isMac = process.platform === 'darwin';

test('loadFsevents rejects non-macOS platforms', { skip: isMac }, () => {
  assert.throws(loadFsevents, /only available on macOS/);
});

test('watch reports a created file', { skip: !isMac, timeout: 10_000 }, async () => {
  const dir = await mkdtemp(join(tmpdir(), 'mac-fswatch-'));
  const file = join(dir, 'hello.txt');
  let stop;
  try {
    const seen = new Promise((res) => {
      stop = watch(dir, (e) => {
        if (e.path.endsWith('hello.txt') && e.event === 'created') res(e);
      });
    });
    await new Promise((r) => setTimeout(r, 200)); // let the FSEvents stream start
    await writeFile(file, 'hi');
    const event = await seen;
    assert.equal(event.type, 'file');
  } finally {
    await stop?.();
    await rm(dir, { recursive: true, force: true });
  }
});
