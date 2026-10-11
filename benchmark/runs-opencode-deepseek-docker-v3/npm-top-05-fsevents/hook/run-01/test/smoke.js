import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { watch, writeSnapshot, getEventsSince } from '../src/watcher.js';

const tmp = await fs.mkdtemp(path.join(os.tmpdir(), 'macos-watch-'));
const watched = path.join(tmp, 'watched');
const snapshot = path.join(tmp, '.snapshot');
await fs.mkdir(watched);

try {
  await writeSnapshot(watched, snapshot);
  await fs.writeFile(path.join(watched, 'created.txt'), 'hello');

  const events = await getEventsSince(watched, snapshot);
  assert.ok(
    events.some((event) => event.type === 'create' && event.path.endsWith('created.txt')),
    'expected a create event from the snapshot diff',
  );

  let subscription;
  const received = await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('timed out waiting for event')), 5000);

    watch(watched, (error, batch) => {
      if (error) {
        clearTimeout(timeout);
        reject(error);
        return;
      }
      if (batch.some((event) => event.path.endsWith('live.txt'))) {
        clearTimeout(timeout);
        resolve(batch);
      }
    })
      .then(async (handle) => {
        subscription = handle;
        await fs.writeFile(path.join(watched, 'live.txt'), 'live');
      })
      .catch((error) => {
        clearTimeout(timeout);
        reject(error);
      });
  });

  assert.ok(received.length > 0, 'expected live subscription events');
  await subscription.unsubscribe();
  console.log('smoke test passed');
} finally {
  await fs.rm(tmp, { recursive: true, force: true });
}
