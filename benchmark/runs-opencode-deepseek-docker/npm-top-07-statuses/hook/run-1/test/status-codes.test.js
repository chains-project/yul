import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { STATUS_CODES, reasonPhrase, codeFor, isError } from '../src/status-codes.js';
import { createServer } from '../src/server.js';

test('reasonPhrase returns standard phrases', () => {
  assert.equal(reasonPhrase(200), 'OK');
  assert.equal(reasonPhrase(404), 'Not Found');
  assert.equal(reasonPhrase(418), "I'm a Teapot");
  assert.equal(reasonPhrase(511), 'Network Authentication Required');
  assert.equal(reasonPhrase(999), undefined);
});

test('codeFor is case-insensitive', () => {
  assert.equal(codeFor('not found'), 404);
  assert.equal(codeFor('NOT FOUND'), 404);
  assert.equal(codeFor('Nope'), undefined);
});

test('isError detects 4xx and 5xx', () => {
  assert.equal(isError(404), true);
  assert.equal(isError(500), true);
  assert.equal(isError(200), false);
});

test('table matches Node built-in http.STATUS_CODES', () => {
  assert.deepEqual(STATUS_CODES, http.STATUS_CODES);
});

test('server responds with reason phrase for a code', async (t) => {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, resolve));
  t.after(() => server.close());

  const { port } = server.address();
  const res = await fetch(`http://127.0.0.1:${port}/status/404`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { code: 404, phrase: 'Not Found' });
});
