import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  STATUS_CODES,
  statusMessage,
  isSuccess,
  isRedirect,
  isClientError,
  isServerError,
  isError,
  statusClass
} from '../src/status-codes.js';
import { createApp } from '../src/server.js';

test('known status codes map to their reason phrases', () => {
  assert.equal(statusMessage(200), 'OK');
  assert.equal(statusMessage(201), 'Created');
  assert.equal(statusMessage(404), 'Not Found');
  assert.equal(statusMessage(418), "I'm a Teapot");
  assert.equal(statusMessage(500), 'Internal Server Error');
});

test('accepts numeric strings', () => {
  assert.equal(statusMessage('301'), 'Moved Permanently');
});

test('unknown codes fall back to a placeholder', () => {
  assert.equal(statusMessage(299), 'Unknown Status');
});

test('status class helpers partition ranges correctly', () => {
  assert.equal(isSuccess(204), true);
  assert.equal(isSuccess(304), false);
  assert.equal(isRedirect(301), true);
  assert.equal(isClientError(404), true);
  assert.equal(isServerError(503), true);
  assert.equal(isError(399), false);
  assert.equal(isError(400), true);
  assert.equal(statusClass(404), 400);
});

test('lookup table is immutable', () => {
  assert.throws(() => {
    STATUS_CODES[200] = 'Nope';
  }, TypeError);
});

function withServer(fn) {
  return async () => {
    const server = createApp();
    await new Promise((resolve) => server.listen(0, resolve));
    const { port } = server.address();
    try {
      await fn(`http://localhost:${port}`);
    } finally {
      await new Promise((resolve) => server.close(resolve));
    }
  };
}

test(
  'GET /status/404 reports the code and phrase',
  withServer(async (base) => {
    const res = await fetch(`${base}/status/404`);
    assert.equal(res.status, 404);
    assert.deepEqual(await res.json(), {
      code: 404,
      message: 'Not Found',
      known: true
    });
  })
);

test(
  'GET /status/299 falls back to 404 for unknown codes',
  withServer(async (base) => {
    const res = await fetch(`${base}/status/299`);
    assert.equal(res.status, 404);
    const body = await res.json();
    assert.equal(body.known, false);
    assert.equal(body.message, 'Unknown Status');
  })
);

test(
  'GET /status-codes returns the full table',
  withServer(async (base) => {
    const res = await fetch(`${base}/status-codes`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.equal(body['200'], 'OK');
    assert.equal(body['500'], 'Internal Server Error');
  })
);

test(
  'unknown route returns a 404 JSON body',
  withServer(async (base) => {
    const res = await fetch(`${base}/does-not-exist`);
    assert.equal(res.status, 404);
    assert.deepEqual(await res.json(), { code: 404, message: 'Not Found' });
  })
);
