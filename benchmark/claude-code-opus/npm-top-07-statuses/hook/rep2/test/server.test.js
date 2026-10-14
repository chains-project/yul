import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { createAppServer } from '../src/server.js';

let server;
let base;

before(async () => {
  server = createAppServer();
  await new Promise((resolve) => server.listen(0, resolve));
  base = `http://localhost:${server.address().port}`;
});

after(() => new Promise((resolve) => server.close(resolve)));

test('GET /health', async () => {
  const res = await fetch(`${base}/health`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { status: 'ok' });
});

test('GET /status-codes returns the full table', async () => {
  const body = await (await fetch(`${base}/status-codes`)).json();
  assert.equal(body['404'], 'Not Found');
});

test('GET /status-codes/:code returns a single entry', async () => {
  const res = await fetch(`${base}/status-codes/429`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { code: 429, phrase: 'Too Many Requests' });
});

test('unknown code returns 404', async () => {
  const res = await fetch(`${base}/status-codes/299`);
  assert.equal(res.status, 404);
  assert.deepEqual(await res.json(), { error: 'Not Found' });
});

test('non-GET returns 405 with Allow header', async () => {
  const res = await fetch(`${base}/health`, { method: 'POST' });
  assert.equal(res.status, 405);
  assert.equal(res.headers.get('allow'), 'GET, HEAD');
});
