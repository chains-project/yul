'use strict'

const assert = require('node:assert/strict')
const { test } = require('node:test')
const { PassThrough, Readable, Stream, Writable } = require('node:stream')
const unpipe = require('../src/unpipe')

function collector () {
  const chunks = []
  const stream = new Writable({
    write (chunk, encoding, callback) {
      chunks.push(chunk.toString())
      callback()
    }
  })
  return { stream, chunks }
}

test('throws without a stream', () => {
  assert.throws(() => unpipe(), TypeError)
})

test('unpipes a modern readable from every destination', () => {
  const source = new PassThrough()
  const a = collector()
  const b = collector()
  const c = collector()

  source.pipe(a.stream)
  source.pipe(b.stream)
  source.pipe(c.stream)
  assert.equal(source.listenerCount('data'), 3)

  unpipe(source)

  assert.equal(source.readableFlowing, false)
  assert.equal(source.listenerCount('data'), 0)
  for (const dest of [a.stream, b.stream, c.stream]) {
    assert.equal(dest.listenerCount('unpipe'), 0)
  }

  source.write('after')
  assert.deepEqual([a.chunks, b.chunks, c.chunks], [[], [], []])
})

test('is a no-op on a stream with no destinations', () => {
  const source = Readable.from(['x'])
  assert.doesNotThrow(() => unpipe(source))
})

test('unpipes a legacy stream from every destination', () => {
  const source = new Stream()
  source.readable = true
  const received = []
  const makeDest = () => {
    const dest = new Stream()
    dest.writable = true
    dest.write = (chunk) => { received.push(chunk); return true }
    dest.end = () => {}
    return dest
  }

  Stream.prototype.pipe.call(source, makeDest())
  Stream.prototype.pipe.call(source, makeDest())
  source.emit('data', 'before')
  assert.deepEqual(received, ['before', 'before'])

  unpipe(source)

  assert.equal(source.listenerCount('data'), 0)
  source.emit('data', 'after')
  assert.deepEqual(received, ['before', 'before'])
})

test('leaves unrelated close listeners on legacy streams alone', () => {
  const source = new Stream()
  source.readable = true
  let closed = false
  source.on('close', function onUserClose () { closed = true })

  unpipe(source)

  assert.equal(closed, false)
  assert.equal(source.listenerCount('close'), 1)
})
