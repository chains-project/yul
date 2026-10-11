'use strict'

var test = require('node:test')
var assert = require('node:assert')
var setPrototype = require('./index.js')

test('sets the prototype of an object', function () {
  var proto = { greet: function () { return 'hi' } }
  var obj = setPrototype({}, proto)

  assert.strictEqual(Object.getPrototypeOf(obj), proto)
  assert.strictEqual(obj.greet(), 'hi')
})

test('returns the same object it was given', function () {
  var obj = {}

  assert.strictEqual(setPrototype(obj, {}), obj)
})

test('supports a null prototype', function () {
  var obj = setPrototype({ a: 1 }, null)

  assert.strictEqual(Object.getPrototypeOf(obj), null)
  assert.strictEqual(obj.a, 1)
})

test('supports functions as targets', function () {
  var proto = { tag: 'proto' }
  var fn = setPrototype(function () {}, proto)

  assert.strictEqual(Object.getPrototypeOf(fn), proto)
})
