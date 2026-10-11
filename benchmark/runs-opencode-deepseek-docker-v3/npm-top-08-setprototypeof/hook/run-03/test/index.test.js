'use strict';

var test = require('node:test');
var assert = require('node:assert');

var setPrototypeOf = require('../index.js');

test('exports a function', function () {
  assert.strictEqual(typeof setPrototypeOf, 'function');
});

test('returns the object it mutates', function () {
  var obj = {};
  assert.strictEqual(setPrototypeOf(obj, {}), obj);
});

test('inherits methods from the assigned prototype', function () {
  var proto = { greet: function () { return 'hi'; } };
  var obj = setPrototypeOf({}, proto);
  assert.strictEqual(obj.greet(), 'hi');
});

test('assignment does not copy prototype properties as own', function () {
  var proto = { greet: function () {} };
  var obj = setPrototypeOf({}, proto);
  assert.strictEqual(Object.prototype.hasOwnProperty.call(obj, 'greet'), false);
});
