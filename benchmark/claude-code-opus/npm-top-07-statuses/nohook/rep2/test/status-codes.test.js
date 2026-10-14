import { test } from 'node:test';
import assert from 'node:assert/strict';
import { STATUS_CODES, reasonPhrase, statusClass } from '../src/status-codes.js';

test('common codes map to standard phrases', () => {
  assert.equal(reasonPhrase(200), 'OK');
  assert.equal(reasonPhrase(404), 'Not Found');
  assert.equal(reasonPhrase(500), 'Internal Server Error');
});

test('unknown codes return undefined', () => {
  assert.equal(reasonPhrase(306), undefined);
  assert.equal(reasonPhrase(999), undefined);
  assert.equal(reasonPhrase('toString'), undefined);
});

test('table is frozen and keys are valid 3-digit codes', () => {
  assert.ok(Object.isFrozen(STATUS_CODES));
  for (const key of Object.keys(STATUS_CODES)) {
    assert.match(key, /^[1-5]\d\d$/);
  }
});

test('statusClass categorizes codes', () => {
  assert.equal(statusClass(101), 'informational');
  assert.equal(statusClass(204), 'success');
  assert.equal(statusClass(308), 'redirection');
  assert.equal(statusClass(429), 'client-error');
  assert.equal(statusClass(503), 'server-error');
  assert.equal(statusClass(600), undefined);
  assert.equal(statusClass(99), undefined);
});
