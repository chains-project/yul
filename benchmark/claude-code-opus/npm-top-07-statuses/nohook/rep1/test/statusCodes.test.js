import { test } from 'node:test';
import assert from 'node:assert/strict';
import { STATUS_CODES, getReasonPhrase, isKnownStatus } from '../src/statusCodes.js';

test('maps common codes to standard reason phrases', () => {
  assert.equal(STATUS_CODES[200], 'OK');
  assert.equal(STATUS_CODES[201], 'Created');
  assert.equal(STATUS_CODES[204], 'No Content');
  assert.equal(STATUS_CODES[301], 'Moved Permanently');
  assert.equal(STATUS_CODES[404], 'Not Found');
  assert.equal(STATUS_CODES[418], "I'm a Teapot");
  assert.equal(STATUS_CODES[500], 'Internal Server Error');
  assert.equal(STATUS_CODES[503], 'Service Unavailable');
});

test('table is frozen', () => {
  assert.ok(Object.isFrozen(STATUS_CODES));
});

test('getReasonPhrase accepts numbers and strings', () => {
  assert.equal(getReasonPhrase(404), 'Not Found');
  assert.equal(getReasonPhrase('404'), 'Not Found');
  assert.equal(getReasonPhrase(999), undefined);
});

test('isKnownStatus', () => {
  assert.equal(isKnownStatus(200), true);
  assert.equal(isKnownStatus(299), false);
});
