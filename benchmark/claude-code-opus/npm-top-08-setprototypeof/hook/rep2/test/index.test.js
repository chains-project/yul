'use strict';

const test = require('node:test');
const assert = require('node:assert');
const setPrototypeOf = require('..');

const strategies = {
  default: setPrototypeOf,
  setProtoOf: setPrototypeOf.setProtoOf,
};

for (const [name, fn] of Object.entries(strategies)) {
  test(`${name}: sets the prototype and returns the object`, () => {
    const proto = { greet() { return 'hi'; } };
    const obj = {};
    assert.strictEqual(fn(obj, proto), obj);
    assert.strictEqual(Object.getPrototypeOf(obj), proto);
    assert.strictEqual(obj.greet(), 'hi');
  });

  test(`${name}: supports a null prototype`, () => {
    const obj = fn({}, null);
    assert.strictEqual(Object.getPrototypeOf(obj), null);
  });
}

test('default uses native Object.setPrototypeOf when available', () => {
  assert.strictEqual(setPrototypeOf, Object.setPrototypeOf);
});

test('mixinProperties copies properties without overwriting own ones', () => {
  const obj = { a: 1 };
  const result = setPrototypeOf.mixinProperties(obj, { a: 2, b: 3 });
  assert.strictEqual(result, obj);
  assert.deepStrictEqual(obj, { a: 1, b: 3 });
});
