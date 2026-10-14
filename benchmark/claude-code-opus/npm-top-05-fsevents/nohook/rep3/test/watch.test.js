import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, realpath, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

test('reports file creation', { skip: process.platform !== 'darwin' && 'FSEvents is macOS-only' }, async () => {
  const { watch } = await import('../src/index.js');
  // FSEvents reports canonical paths (/private/var/... rather than /var/...).
  const dir = await realpath(await mkdtemp(join(tmpdir(), 'mac-fswatch-')));
  const target = join(dir, 'hello.txt');

  const seen = new Promise((resolve) => {
    const stop = watch(dir, async (e) => {
      if (e.path === target && e.event === 'created') {
        await stop();
        resolve(e);
      }
    });
  });

  // Give the stream a moment to start before generating events.
  await new Promise((r) => setTimeout(r, 200));
  await writeFile(target, 'hi');

  const event = await seen;
  assert.equal(event.type, 'file');
  assert.equal(typeof event.id, 'number');
  await rm(dir, { recursive: true, force: true });
});
