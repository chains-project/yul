'use strict';

var test = require('node:test');
var assert = require('node:assert');
var fallback = require('../lib/fallback');

test('exposes a resolved fallback function', function () {
  assert.strictEqual(typeof fallback, 'function');
});

test('viaAccessor sets the prototype', function () {
  var proto = { hi: true };
  var obj = fallback.viaAccessor({}, proto);
  assert.strictEqual(Object.getPrototypeOf(obj), proto);
});

test('viaMixing copies inherited properties without overriding own ones', function () {
  var proto = { b: 2, c: 3 };
  var obj = fallback.viaMixing({ a: 1, b: 9 }, proto);
  assert.strictEqual(obj.a, 1);
  assert.strictEqual(obj.b, 9);
  assert.strictEqual(obj.c, 3);
});

test('viaMixing copies non-enumerable properties', function () {
  var proto = {};
  Object.defineProperty(proto, 'hidden', { value: 7, enumerable: false });
  var obj = fallback.viaMixing({}, proto);
  assert.strictEqual(obj.hidden, 7);
});
