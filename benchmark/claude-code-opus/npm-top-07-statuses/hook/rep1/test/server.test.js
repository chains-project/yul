import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from '../src/server.js';

let server;
let base;

before(async () => {
  server = createServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  base = `http://127.0.0.1:${server.address().port}`;
});

after(() => new Promise((resolve) => server.close(resolve)));

test('GET /health', async () => {
  const res = await fetch(`${base}/health`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { status: 'ok' });
});

test('GET /status-codes/:code returns the reason phrase', async () => {
  const res = await fetch(`${base}/status-codes/404`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { code: 404, reason: 'Not Found', class: 'client_error' });
});

test('GET /status-codes/:code with unknown code is 404', async () => {
  const res = await fetch(`${base}/status-codes/299`);
  assert.equal(res.status, 404);
  assert.equal(res.statusText, 'Not Found');
});

test('GET /status-codes lists the table', async () => {
  const body = await (await fetch(`${base}/status-codes`)).json();
  assert.equal(body['503'], 'Service Unavailable');
});

test('non-GET is 405 with Allow header', async () => {
  const res = await fetch(`${base}/health`, { method: 'POST' });
  assert.equal(res.status, 405);
  assert.equal(res.headers.get('allow'), 'GET, HEAD');
});
