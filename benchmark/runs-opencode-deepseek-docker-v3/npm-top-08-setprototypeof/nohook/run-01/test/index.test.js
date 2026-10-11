'use strict'

var test = require('node:test')
var assert = require('node:assert')
var setPrototypeOf = require('..')

test('exports a function', function () {
  assert.strictEqual(typeof setPrototypeOf, 'function')
})

test('sets the prototype of an object', function () {
  var proto = { hello: 'world' }
  var obj = setPrototypeOf({}, proto)

  assert.strictEqual(Object.getPrototypeOf(obj), proto)
  assert.strictEqual(obj.hello, 'world')
})

test('returns the same object', function () {
  var obj = {}
  assert.strictEqual(setPrototypeOf(obj, {}), obj)
})

test('inherits properties from the new prototype', function () {
  function Base () {}
  Base.prototype.greet = function () { return 'hi' }

  var obj = setPrototypeOf({}, Base.prototype)
  assert.strictEqual(obj.greet(), 'hi')
})

test('existing own properties are preserved', function () {
  var obj = setPrototypeOf({ own: 1 }, { inherited: 2 })
  assert.strictEqual(obj.own, 1)
  assert.strictEqual(obj.inherited, 2)
})

test('can set prototype to null', function () {
  var obj = setPrototypeOf({}, null)
  assert.strictEqual(Object.getPrototypeOf(obj), null)
})
