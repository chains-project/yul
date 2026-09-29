'use strict';

const test = require('node:test');
const assert = require('node:assert');

const index = require.resolve('../index.js');
const setPrototypeOf = require(index);

test('exports a function', () => {
  assert.strictEqual(typeof setPrototypeOf, 'function');
});

test('returns the same object it was given', () => {
  const obj = {};
  const result = setPrototypeOf(obj, {});
  assert.strictEqual(result, obj);
});

test('sets a prototype that is visible via getPrototypeOf', () => {
  const proto = { greet() { return 'hi'; } };
  const obj = setPrototypeOf({}, proto);
  assert.strictEqual(Object.getPrototypeOf(obj), proto);
  assert.strictEqual(obj.greet(), 'hi');
});

test('participates in the prototype chain for instanceof', () => {
  function Base() {}
  const obj = setPrototypeOf({}, Base.prototype);
  assert.ok(obj instanceof Base);
});

test('accepts null as a prototype', () => {
  const obj = setPrototypeOf({}, null);
  assert.strictEqual(Object.getPrototypeOf(obj), null);
});

test('works when Object.setPrototypeOf is unavailable', () => {
  const original = Object.setPrototypeOf;

  try {
    Object.setPrototypeOf = undefined;
    delete require.cache[index];

    const fallback = require(index);
    const proto = { flag: true };
    const obj = fallback({}, proto);

    assert.strictEqual(Object.getPrototypeOf(obj), proto);
  } finally {
    Object.setPrototypeOf = original;
    delete require.cache[index];
  }
});
