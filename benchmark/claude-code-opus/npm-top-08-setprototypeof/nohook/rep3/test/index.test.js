'use strict';

const test = require('node:test');
const assert = require('node:assert');
const setPrototypeOf = require('..');
const { setProtoOf, mixinProperties } = setPrototypeOf;

test('uses native Object.setPrototypeOf when available', () => {
  assert.strictEqual(setPrototypeOf, Object.setPrototypeOf);
});

test('sets the prototype and returns the object', () => {
  const proto = { greet() { return 'hi'; } };
  const obj = {};
  assert.strictEqual(setPrototypeOf(obj, proto), obj);
  assert.strictEqual(Object.getPrototypeOf(obj), proto);
  assert.strictEqual(obj.greet(), 'hi');
});

test('supports a null prototype', () => {
  const obj = setPrototypeOf({}, null);
  assert.strictEqual(Object.getPrototypeOf(obj), null);
});

test('__proto__ fallback sets the prototype', () => {
  const proto = { a: 1 };
  const obj = setProtoOf({}, proto);
  assert.strictEqual(Object.getPrototypeOf(obj), proto);
});

test('mixin fallback copies properties without overwriting own ones', () => {
  const obj = mixinProperties({ a: 'own' }, { a: 'proto', b: 2 });
  assert.deepStrictEqual(obj, { a: 'own', b: 2 });
});
