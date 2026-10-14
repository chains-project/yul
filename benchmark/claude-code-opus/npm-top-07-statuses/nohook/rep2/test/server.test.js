import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from '../src/server.js';

let server;
let base;

before(async () => {
  server = createServer();
  await new Promise((resolve) => server.listen(0, resolve));
  base = `http://localhost:${server.address().port}`;
});

after(() => new Promise((resolve) => server.close(resolve)));

test('GET /health', async () => {
  const res = await fetch(`${base}/health`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { status: 'ok' });
});

test('GET /status-codes/:code', async () => {
  const res = await fetch(`${base}/status-codes/418`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { code: 418, phrase: "I'm a Teapot" });
});

test('unknown code returns 404 with reason phrase', async () => {
  const res = await fetch(`${base}/status-codes/299`);
  assert.equal(res.status, 404);
  assert.equal(res.statusText, 'Not Found');
});

test('non-GET returns 405 with Allow header', async () => {
  const res = await fetch(`${base}/health`, { method: 'POST' });
  assert.equal(res.status, 405);
  assert.equal(res.headers.get('allow'), 'GET, HEAD');
});
