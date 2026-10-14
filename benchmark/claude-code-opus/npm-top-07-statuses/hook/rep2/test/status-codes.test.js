import { test } from 'node:test';
import assert from 'node:assert/strict';
import { STATUS_CODES, getReasonPhrase, isKnownStatus } from '../src/status-codes.js';

test('maps common codes to standard reason phrases', () => {
  assert.equal(STATUS_CODES[200], 'OK');
  assert.equal(STATUS_CODES[201], 'Created');
  assert.equal(STATUS_CODES[301], 'Moved Permanently');
  assert.equal(STATUS_CODES[404], 'Not Found');
  assert.equal(STATUS_CODES[418], "I'm a Teapot");
  assert.equal(STATUS_CODES[500], 'Internal Server Error');
});

test('table is frozen', () => {
  assert.ok(Object.isFrozen(STATUS_CODES));
});

test('getReasonPhrase accepts numbers and numeric strings', () => {
  assert.equal(getReasonPhrase(404), 'Not Found');
  assert.equal(getReasonPhrase('503'), 'Service Unavailable');
});

test('unknown or invalid codes return undefined', () => {
  assert.equal(getReasonPhrase(299), undefined);
  assert.equal(getReasonPhrase('abc'), undefined);
  assert.equal(getReasonPhrase(200.5), undefined);
  assert.equal(isKnownStatus(999), false);
  assert.equal(isKnownStatus(204), true);
});
