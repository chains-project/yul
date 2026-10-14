import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { watch, loadFsevents } from '../src/index.js';

const isMac = process.platform === 'darwin';

test('loadFsevents rejects non-macOS platforms', { skip: isMac }, () => {
  assert.throws(() => loadFsevents(), /only available on macOS/);
});

test('reports a created file', { skip: !isMac, timeout: 10_000 }, async () => {
  const dir = await mkdtemp(path.join(tmpdir(), 'mac-watch-'));
  const file = path.join(dir, 'hello.txt');
  const watcher = watch(dir);
  try {
    const seen = new Promise((resolve) => {
      watcher.on('change', (e) => {
        if (e.path.endsWith('hello.txt')) resolve(e);
      });
    });
    // FSEvents needs a moment to start delivering events.
    await new Promise((r) => setTimeout(r, 200));
    await writeFile(file, 'hi');
    const event = await seen;
    assert.equal(event.type, 'file');
  } finally {
    await watcher.close();
    await rm(dir, { recursive: true, force: true });
  }
});
