import assert from 'node:assert/strict';
import test from 'node:test';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { watch, nativeAvailable, FLAG_NAMES } from '../src/index.js';

test('reports native availability', () => {
  assert.equal(typeof nativeAvailable(), 'boolean');
});

test('exposes FSEvents flag names', () => {
  assert.equal(FLAG_NAMES[0], 'None');
  assert.ok(FLAG_NAMES.includes('ItemCreated'));
  assert.ok(FLAG_NAMES.includes('ItemIsDir'));
});

test('emits a change for a new file', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'watch-'));
  const watcher = watch(dir, { latency: 0.05 });
  try {
    const event = await new Promise((resolve, reject) => {
      watcher.once('event', resolve);
      const timer = setTimeout(() => reject(new Error('no event received')), 5000);
      timer.unref?.();
      watcher.once('error', reject);
      writeFile(join(dir, 'created.txt'), 'hello');
    });

    assert.match(event.path, /created\.txt$/);
    assert.equal(typeof event.native, 'boolean');
    if (event.native) {
      assert.ok(event.flagNames.includes('ItemCreated'));
      assert.equal(event.type, 'file');
    }
  } finally {
    watcher.close();
    await rm(dir, { recursive: true, force: true });
  }
});
