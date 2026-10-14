'use strict';

const test = require('node:test');
const assert = require('node:assert');
const setPrototypeOf = require('..');

test('sets the prototype and returns the object', () => {
  const proto = { greet() { return 'hi'; } };
  const obj = {};
  assert.strictEqual(setPrototypeOf(obj, proto), obj);
  assert.strictEqual(Object.getPrototypeOf(obj), proto);
  assert.strictEqual(obj.greet(), 'hi');
});

test('accepts null', () => {
  const obj = setPrototypeOf({}, null);
  assert.strictEqual(Object.getPrototypeOf(obj), null);
});

test('named export matches default', () => {
  assert.strictEqual(setPrototypeOf.setPrototypeOf, setPrototypeOf);
});

test('does not mutate the built-in Object.setPrototypeOf', () => {
  assert.notStrictEqual(setPrototypeOf, Object.setPrototypeOf);
  assert.strictEqual(Object.setPrototypeOf.setPrototypeOf, undefined);
});
