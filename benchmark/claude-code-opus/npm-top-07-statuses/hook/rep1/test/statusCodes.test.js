import { test } from 'node:test';
import assert from 'node:assert/strict';
import { STATUS_CODES, getReasonPhrase, getStatusClass } from '../src/statusCodes.js';

test('common codes map to standard reason phrases', () => {
  assert.equal(getReasonPhrase(200), 'OK');
  assert.equal(getReasonPhrase(404), 'Not Found');
  assert.equal(getReasonPhrase('500'), 'Internal Server Error');
  assert.equal(getReasonPhrase(422), 'Unprocessable Content');
});

test('unknown codes return undefined', () => {
  assert.equal(getReasonPhrase(299), undefined);
  assert.equal(getReasonPhrase(418), undefined);
  assert.equal(getReasonPhrase('toString'), undefined);
});

test('table is frozen and keys are valid 3-digit codes', () => {
  assert.ok(Object.isFrozen(STATUS_CODES));
  for (const key of Object.keys(STATUS_CODES)) {
    assert.match(key, /^[1-5]\d{2}$/);
  }
});

test('getStatusClass', () => {
  assert.equal(getStatusClass(101), 'informational');
  assert.equal(getStatusClass(204), 'success');
  assert.equal(getStatusClass(308), 'redirection');
  assert.equal(getStatusClass(429), 'client_error');
  assert.equal(getStatusClass(503), 'server_error');
  assert.equal(getStatusClass(600), undefined);
  assert.equal(getStatusClass(99), undefined);
});
