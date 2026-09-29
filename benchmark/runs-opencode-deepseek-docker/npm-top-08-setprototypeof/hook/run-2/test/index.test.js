'use strict';

var test = require('node:test');
var assert = require('node:assert/strict');
var setPrototypeOf = require('..');

test('sets the prototype and returns the same object', function () {
  var proto = { greet: function () { return 'hello'; } };
  var obj = {};
  var result = setPrototypeOf(obj, proto);
  assert.equal(result, obj);
  assert.equal(Object.getPrototypeOf(obj), proto);
  assert.equal(obj.greet(), 'hello');
});

test('accepts null as a prototype', function () {
  var obj = { a: 1 };
  setPrototypeOf(obj, null);
  assert.equal(Object.getPrototypeOf(obj), null);
  assert.equal(obj.a, 1);
});

test('works with functions', function () {
  var proto = { describe: function () { return 'callable'; } };
  function fn() {}
  setPrototypeOf(fn, proto);
  assert.equal(Object.getPrototypeOf(fn), proto);
  assert.equal(fn.describe(), 'callable');
});

test('returns primitives unchanged', function () {
  assert.equal(setPrototypeOf(1, {}), 1);
  assert.equal(setPrototypeOf('x', {}), 'x');
  assert.equal(setPrototypeOf(true, {}), true);
});

test('throws when the target is null or undefined', function () {
  assert.throws(function () { setPrototypeOf(null, {}); }, TypeError);
  assert.throws(function () { setPrototypeOf(undefined, {}); }, TypeError);
});

test('throws when the prototype is not an object or null', function () {
  assert.throws(function () { setPrototypeOf({}, 42); }, TypeError);
  assert.throws(function () { setPrototypeOf({}, 'nope'); }, TypeError);
  assert.throws(function () { setPrototypeOf({}, undefined); }, TypeError);
});

test('exposes the selected strategy', function () {
  assert.ok(['native', '__proto__', 'copy'].indexOf(setPrototypeOf.strategy) !== -1);
});

test('can extend a chain repeatedly', function () {
  var a = { a: 1 };
  var b = { b: 2 };
  var c = { c: 3 };
  setPrototypeOf(a, b);
  setPrototypeOf(b, c);
  assert.equal(a.a, 1);
  assert.equal(a.b, 2);
  assert.equal(a.c, 3);
  assert.equal(Object.getPrototypeOf(Object.getPrototypeOf(a)), c);
});
