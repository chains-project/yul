import { test } from 'node:test';
import assert from 'node:assert/strict';
import { STATUS_CODES, reasonPhrase, isKnownStatus } from '../src/status-codes.js';

test('maps common codes to standard reason phrases', () => {
  assert.equal(reasonPhrase(200), 'OK');
  assert.equal(reasonPhrase(201), 'Created');
  assert.equal(reasonPhrase(204), 'No Content');
  assert.equal(reasonPhrase(301), 'Moved Permanently');
  assert.equal(reasonPhrase(400), 'Bad Request');
  assert.equal(reasonPhrase(404), 'Not Found');
  assert.equal(reasonPhrase(500), 'Internal Server Error');
  assert.equal(reasonPhrase(503), 'Service Unavailable');
});

test('unknown codes return undefined', () => {
  assert.equal(reasonPhrase(299), undefined);
  assert.equal(isKnownStatus(299), false);
  assert.equal(isKnownStatus(418), true);
});

test('table is frozen and keyed by number', () => {
  assert.ok(Object.isFrozen(STATUS_CODES));
  assert.throws(() => { STATUS_CODES[200] = 'Changed'; }, TypeError);
});
