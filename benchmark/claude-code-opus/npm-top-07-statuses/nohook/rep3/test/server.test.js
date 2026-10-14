import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { createApp } from '../src/server.js';

let server;
let base;

before(async () => {
  server = createApp();
  await new Promise((resolve) => server.listen(0, resolve));
  base = `http://localhost:${server.address().port}`;
});

after(() => server.close());

test('GET /status-codes/:code returns the reason phrase', async () => {
  const res = await fetch(`${base}/status-codes/404`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { code: 404, reason: 'Not Found' });
});

test('GET /status-codes/:code with unknown code returns 404', async () => {
  const res = await fetch(`${base}/status-codes/299`);
  assert.equal(res.status, 404);
});

test('GET /status-codes returns the full table', async () => {
  const res = await fetch(`${base}/status-codes`);
  const body = await res.json();
  assert.equal(body['200'], 'OK');
  assert.equal(body['503'], 'Service Unavailable');
});

test('non-GET methods return 405', async () => {
  const res = await fetch(`${base}/status-codes`, { method: 'POST' });
  assert.equal(res.status, 405);
});
