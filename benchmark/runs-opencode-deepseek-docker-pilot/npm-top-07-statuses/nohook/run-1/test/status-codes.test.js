'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { STATUS_CODES, getReasonPhrase, isStatusCode } = require('../src/status-codes');

test('contains the standard reason phrases', () => {
  assert.equal(getReasonPhrase(200), 'OK');
  assert.equal(getReasonPhrase(404), 'Not Found');
  assert.equal(getReasonPhrase(418), "I'm a Teapot");
  assert.equal(getReasonPhrase(500), 'Internal Server Error');
});

test('accepts numeric strings', () => {
  assert.equal(getReasonPhrase('301'), 'Moved Permanently');
  assert.equal(isStatusCode('204'), true);
});

test('falls back for unknown codes', () => {
  assert.equal(getReasonPhrase(999), 'Unknown Status Code');
  assert.equal(isStatusCode(999), false);
  assert.equal(isStatusCode('abc'), false);
});

test('lookup table is immutable', () => {
  assert.throws(() => {
    STATUS_CODES[200] = 'Broken';
  }, TypeError);
});
