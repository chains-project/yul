import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { Watcher } from '../src/index.js';

const isMac = process.platform === 'darwin';

test('throws a clear error on non-macOS platforms', { skip: isMac }, () => {
  assert.throws(() => new Watcher('.').start(), /only available on macOS/);
});

test('reports file creation', { skip: !isMac, timeout: 10_000 }, async () => {
  // realpath: FSEvents reports /private/var/... rather than the /var symlink
  const dir = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'mac-fswatch-')));
  const target = path.join(dir, 'hello.txt');
  const watcher = new Watcher(dir).start();
  try {
    const seen = new Promise((resolve) => {
      watcher.on('change', (e) => {
        if (e.path === target && e.event === 'created') resolve(e);
      });
    });
    // Give FSEvents a moment to register the stream before writing.
    await new Promise((r) => setTimeout(r, 200));
    await fs.writeFile(target, 'hi');
    const event = await seen;
    assert.equal(event.type, 'file');
  } finally {
    await watcher.stop();
    await fs.rm(dir, { recursive: true, force: true });
  }
});
