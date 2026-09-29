'use strict';

var test = require('node:test');
var assert = require('node:assert');
var setPrototypeOf = require('../');

test('returns the same object', function () {
  var obj = {};
  assert.strictEqual(setPrototypeOf(obj, {}), obj);
});

test('sets the prototype of the object', function () {
  var proto = { hello: function () { return 'world'; } };
  var obj = setPrototypeOf({}, proto);
  assert.strictEqual(Object.getPrototypeOf(obj), proto);
  assert.strictEqual(obj.hello(), 'world');
});

test('supports a null prototype', function () {
  var obj = setPrototypeOf({}, null);
  assert.strictEqual(Object.getPrototypeOf(obj), null);
});

test('keeps own properties intact', function () {
  var obj = setPrototypeOf({ a: 1 }, { b: 2 });
  assert.strictEqual(obj.a, 1);
  assert.strictEqual(obj.b, 2);
});

test('returns primitives unchanged', function () {
  assert.strictEqual(setPrototypeOf(1, {}), 1);
  assert.strictEqual(setPrototypeOf('x', {}), 'x');
});

test('rejects invalid prototype values', function () {
  assert.throws(function () {
    setPrototypeOf({}, 42);
  }, TypeError);
});
