import { test } from 'node:test';
import assert from 'node:assert/strict';
import { STATUS_CODES, reasonPhrase, statusClass } from '../src/status-codes.js';

test('looks up common reason phrases', () => {
  assert.equal(reasonPhrase(200), 'OK');
  assert.equal(reasonPhrase(404), 'Not Found');
  assert.equal(reasonPhrase(413), 'Content Too Large');
  assert.equal(reasonPhrase(503), 'Service Unavailable');
});

test('returns undefined for unknown codes and prototype keys', () => {
  assert.equal(reasonPhrase(299), undefined);
  assert.equal(reasonPhrase('toString'), undefined);
});

test('table is frozen and keys are valid 3-digit codes', () => {
  assert.ok(Object.isFrozen(STATUS_CODES));
  for (const key of Object.keys(STATUS_CODES)) {
    const code = Number(key);
    assert.ok(code >= 100 && code <= 599, `bad code ${key}`);
  }
});

test('classifies status codes', () => {
  assert.equal(statusClass(101), 'informational');
  assert.equal(statusClass(204), 'success');
  assert.equal(statusClass(308), 'redirection');
  assert.equal(statusClass(429), 'client_error');
  assert.equal(statusClass(502), 'server_error');
  assert.equal(statusClass(600), undefined);
});
