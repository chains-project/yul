import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm, realpath } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { once } from 'node:events';
import { watch } from '../src/index.js';

test('emits a change event when a file is written', async () => {
  // realpath: on macOS, /var is a symlink to /private/var and FSEvents reports real paths
  const dir = await realpath(await mkdtemp(join(tmpdir(), 'watch-test-')));
  const watcher = watch(dir);
  try {
    // FSEvents needs a moment to start delivering events
    await new Promise((r) => setTimeout(r, 200));
    const file = join(dir, 'hello.txt');
    const changed = once(watcher, 'change');
    await writeFile(file, 'hi');
    const [evt] = await changed;
    assert.equal(evt.path, file);
  } finally {
    await watcher.close();
    await rm(dir, { recursive: true, force: true });
  }
});
