'use strict';

var test = require('node:test');
var assert = require('node:assert');
var setPrototypeOf = require('./index.js');

test('sets the prototype of an object', function () {
  var proto = { hello: function () { return 'world'; } };
  var obj = {};
  var returned = setPrototypeOf(obj, proto);
  assert.strictEqual(returned, obj);
  assert.strictEqual(Object.getPrototypeOf(obj), proto);
  assert.strictEqual(obj.hello(), 'world');
});

test('supports a null prototype', function () {
  var obj = { a: 1 };
  setPrototypeOf(obj, null);
  assert.strictEqual(Object.getPrototypeOf(obj), null);
  assert.strictEqual(obj.a, 1);
});

test('sets the prototype of a function', function () {
  function target() {}
  var proto = { tag: 'fn' };
  setPrototypeOf(target, proto);
  assert.strictEqual(Object.getPrototypeOf(target), proto);
});

test('keeps own properties intact', function () {
  var obj = { b: 2 };
  Object.defineProperty(obj, 'hidden', { value: 3, enumerable: false });
  setPrototypeOf(obj, { c: 4 });
  assert.strictEqual(obj.b, 2);
  assert.strictEqual(obj.hidden, 3);
  assert.strictEqual(obj.c, 4);
});

test('is exposed as a named property for interop', function () {
  assert.strictEqual(setPrototypeOf.setPrototypeOf, setPrototypeOf);
});

test('rejects non-object targets', function () {
  assert.throws(function () { setPrototypeOf(null, {}); }, TypeError);
  assert.throws(function () { setPrototypeOf(1, {}); }, TypeError);
});

test('rejects invalid prototypes', function () {
  assert.throws(function () { setPrototypeOf({}, 1); }, TypeError);
  assert.throws(function () { setPrototypeOf({}, 'x'); }, TypeError);
  assert.doesNotThrow(function () { setPrototypeOf({}, null); });
});
