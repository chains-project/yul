import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from '../src/server.js';

test('echoes the request body', async () => {
  const server = createServer().listen(0);
  await new Promise((r) => server.once('listening', r));
  const { port } = server.address();
  try {
    const res = await fetch(`http://localhost:${port}`, { method: 'POST', body: 'ping' });
    assert.equal(await res.text(), 'ping');
  } finally {
    server.close();
  }
});
