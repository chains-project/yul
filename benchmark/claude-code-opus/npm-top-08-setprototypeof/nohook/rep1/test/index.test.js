'use strict';

const test = require('node:test');
const assert = require('node:assert');
const setPrototypeOf = require('..');
const { setProtoOf, mixinProperties } = setPrototypeOf;

test('uses native Object.setPrototypeOf when available', () => {
  assert.strictEqual(setPrototypeOf, Object.setPrototypeOf);
});

for (const [name, fn] of [['default', setPrototypeOf], ['setProtoOf', setProtoOf]]) {
  test(`${name}: sets the prototype and returns the object`, () => {
    const proto = { greet() { return 'hi'; } };
    const obj = {};
    assert.strictEqual(fn(obj, proto), obj);
    assert.strictEqual(Object.getPrototypeOf(obj), proto);
    assert.strictEqual(obj.greet(), 'hi');
  });

  test(`${name}: supports instanceof`, () => {
    class Foo {}
    assert.ok(fn({}, Foo.prototype) instanceof Foo);
  });
}

test('mixinProperties: copies props without overwriting own props', () => {
  const obj = mixinProperties({ a: 1 }, { a: 2, b: 3 });
  assert.deepStrictEqual(obj, { a: 1, b: 3 });
});
