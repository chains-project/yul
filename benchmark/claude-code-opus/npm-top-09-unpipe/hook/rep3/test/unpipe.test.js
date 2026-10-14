'use strict'

const { test } = require('node:test')
const assert = require('node:assert')
const { Stream, PassThrough, Readable } = require('stream')
const unpipe = require('../src/unpipe')

test('throws without a stream', () => {
  assert.throws(() => unpipe(), TypeError)
})

test('unpipes a Readable from all destinations', () => {
  const src = new Readable({ read () {} })
  const a = new PassThrough()
  const b = new PassThrough()
  src.pipe(a)
  src.pipe(b)

  unpipe(src)

  const received = []
  a.on('data', (c) => received.push(c))
  b.on('data', (c) => received.push(c))
  src.push('hello')
  assert.strictEqual(received.length, 0)
  assert.strictEqual(src.listenerCount('data'), 0)
})

test('unpipes a legacy Stream from all destinations', () => {
  const src = new Stream()
  src.readable = true
  const a = new PassThrough()
  const b = new PassThrough()
  src.pipe(a)
  src.pipe(b)
  assert.strictEqual(src.listenerCount('data'), 2)

  unpipe(src)

  assert.strictEqual(src.listenerCount('data'), 0)
  assert.strictEqual(src.listeners('close').filter((l) => l.name === 'cleanup').length, 0)
})

test('is a no-op on an unpiped legacy Stream', () => {
  const src = new Stream()
  const onClose = () => {}
  src.on('close', onClose)
  unpipe(src)
  assert.deepStrictEqual(src.listeners('close'), [onClose])
})
