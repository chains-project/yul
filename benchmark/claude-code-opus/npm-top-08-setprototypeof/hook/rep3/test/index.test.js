'use strict'

const { test } = require('node:test')
const assert = require('node:assert/strict')
const setPrototypeOf = require('..')

const proto = { greet () { return 'hi' } }

test('sets the prototype and returns the object', () => {
  const obj = {}
  assert.equal(setPrototypeOf(obj, proto), obj)
  assert.equal(Object.getPrototypeOf(obj), proto)
  assert.equal(obj.greet(), 'hi')
})

test('accepts a null prototype', () => {
  const obj = setPrototypeOf({}, null)
  assert.equal(Object.getPrototypeOf(obj), null)
})

test('__proto__ fallback sets the prototype', () => {
  const obj = setPrototypeOf.setProtoOf({}, proto)
  assert.equal(Object.getPrototypeOf(obj), proto)
})

test('mixin fallback copies properties without overwriting own ones', () => {
  const obj = setPrototypeOf.mixinProperties({ greet: 'own' }, { greet: 'x', other: 1 })
  assert.equal(obj.greet, 'own')
  assert.equal(obj.other, 1)
})
