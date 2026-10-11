import test from 'node:test'
import assert from 'node:assert/strict'

import setPrototypeOf, { setPrototypeOf as named } from '../index.js'

test('sets the prototype of an object at runtime', () => {
  const proto = { greet() { return 'hello' } }
  const obj = {}

  setPrototypeOf(obj, proto)

  assert.equal(Object.getPrototypeOf(obj), proto)
  assert.equal(obj.greet(), 'hello')
})

test('returns the object it was given', () => {
  const obj = {}
  assert.equal(setPrototypeOf(obj, null), obj)
})

test('exposes the same function as a named export', () => {
  assert.equal(named, setPrototypeOf)
})
