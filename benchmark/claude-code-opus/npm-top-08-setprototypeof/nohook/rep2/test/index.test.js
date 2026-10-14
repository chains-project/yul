'use strict';

const test = require('node:test');
const assert = require('node:assert');
const setPrototypeOf = require('..');

test('sets the prototype and returns the same object', () => {
  const proto = { greet() { return 'hi'; } };
  const obj = {};
  const result = setPrototypeOf(obj, proto);
  assert.strictEqual(result, obj);
  assert.strictEqual(Object.getPrototypeOf(obj), proto);
  assert.strictEqual(obj.greet(), 'hi');
});

test('accepts null', () => {
  const obj = setPrototypeOf({}, null);
  assert.strictEqual(Object.getPrototypeOf(obj), null);
});

test('throws on invalid prototype', () => {
  assert.throws(() => setPrototypeOf({}, 42), TypeError);
});

test('named export matches default', () => {
  assert.strictEqual(setPrototypeOf.setPrototypeOf, setPrototypeOf);
});
