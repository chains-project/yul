'use strict'

const test = require('node:test')
const assert = require('node:assert/strict')
const { PassThrough } = require('node:stream')

const unpipe = require('../lib/unpipe')

function tick () {
  return new Promise((resolve) => setImmediate(resolve))
}

function collect (stream) {
  const chunks = []
  stream.on('data', (chunk) => chunks.push(chunk.toString()))
  return chunks
}

test('unpipes a stream from every destination', async () => {
  const src = new PassThrough()
  const a = new PassThrough()
  const b = new PassThrough()
  const c = new PassThrough()

  const seen = { a: collect(a), b: collect(b), c: collect(c) }
  const unpiped = []
  a.on('unpipe', () => unpiped.push('a'))
  b.on('unpipe', () => unpiped.push('b'))
  c.on('unpipe', () => unpiped.push('c'))

  src.pipe(a)
  src.pipe(b)
  src.pipe(c)

  assert.equal(src._readableState.pipes.length, 3)

  src.write('before')
  await tick()
  assert.deepEqual(seen, { a: ['before'], b: ['before'], c: ['before'] })

  assert.equal(unpipe(src), src)
  assert.equal(src._readableState.pipes.length, 0)
  assert.deepEqual(unpiped.sort(), ['a', 'b', 'c'])

  src.write('after')
  await tick()
  assert.deepEqual(seen, { a: ['before'], b: ['before'], c: ['before'] })
})

test('is a no-op when nothing is piped', () => {
  const src = new PassThrough()
  assert.equal(unpipe(src), src)
  assert.equal(src._readableState.pipes.length, 0)
})

test('throws when no stream is provided', () => {
  assert.throws(() => unpipe(), TypeError)
})

test('falls back to close-listener cleanup for legacy streams', () => {
  const calls = []

  const legacy = {
    listeners (event) {
      if (event === 'data') {
        return [function ondata () {}]
      }
      if (event === 'close') {
        return [
          function cleanup () { calls.push('cleanup') },
          function onclose () { calls.push('onclose') },
          function unrelated () { calls.push('unrelated') }
        ]
      }
      return []
    }
  }

  unpipe(legacy)
  assert.deepEqual(calls, ['cleanup', 'onclose'])
})

test('legacy fallback does nothing without pipe data listeners', () => {
  const calls = []
  const legacy = {
    listeners (event) {
      if (event === 'close') {
        return [function cleanup () { calls.push('cleanup') }]
      }
      return []
    }
  }

  unpipe(legacy)
  assert.deepEqual(calls, [])
})
