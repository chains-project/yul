import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { createServer } from '../src/server.js';

let server;
let base;

before(async () => {
  server = createServer();
  await new Promise((r) => server.listen(0, r));
  base = `http://localhost:${server.address().port}`;
});

after(() => new Promise((r) => server.close(r)));

test('GET /health', async () => {
  const res = await fetch(`${base}/health`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { status: 'ok' });
});

test('GET /stream streams data and cleans up on client abort', async () => {
  const firstChunk = await new Promise((resolve, reject) => {
    const req = http.get(`${base}/stream`, (res) => {
      assert.equal(res.statusCode, 200);
      res.once('data', (chunk) => {
        req.destroy();
        resolve(chunk.toString());
      });
    });
    req.on('error', (err) => {
      if (err.code !== 'ECONNRESET') reject(err);
    });
  });

  assert.match(firstChunk, /^\d{4}-\d{2}-\d{2}T/);
});

test('unknown route returns 404', async () => {
  const res = await fetch(`${base}/nope`);
  assert.equal(res.status, 404);
});
