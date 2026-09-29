'use strict';

var test = require('node:test');
var assert = require('node:assert');
var setPrototypeOf = require('../');

test('sets the prototype of an object', function () {
  var proto = { hello: 'world' };
  var object = setPrototypeOf({}, proto);

  assert.strictEqual(Object.getPrototypeOf(object), proto);
  assert.strictEqual(object.hello, 'world');
});

test('returns the object it was given', function () {
  var object = {};

  assert.strictEqual(setPrototypeOf(object, {}), object);
});

test('accepts null to detach the prototype', function () {
  var object = setPrototypeOf({ a: 1 }, null);

  assert.strictEqual(Object.getPrototypeOf(object), null);
  assert.strictEqual(object.a, 1);
});

test('exposes the native implementation when present', function () {
  if (Object.setPrototypeOf) {
    assert.strictEqual(setPrototypeOf, Object.setPrototypeOf);
  }
});
