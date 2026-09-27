import test from 'node:test'
import assert from 'node:assert/strict'
import { Readable, Writable, PassThrough } from 'node:stream'
import { unpipeAll } from '../src/stream-utils.js'

function discard(onUnpipe) {
  const dest = new Writable({
    write(_chunk, _enc, callback) {
      callback()
    },
  })
  if (onUnpipe) dest.on('unpipe', onUnpipe)
  return dest
}

test('detaches every destination from a shared source', () => {
  const source = new Readable({ read() {} })
  const unpiped = []
  const a = discard(() => unpiped.push('a'))
  const b = discard(() => unpiped.push('b'))
  const c = discard(() => unpiped.push('c'))

  source.pipe(a)
  source.pipe(b)
  source.pipe(c)

  assert.equal(source._readableState.pipes.length, 3)

  const returned = unpipeAll(source)

  assert.equal(returned, source)
  assert.deepEqual(source._readableState.pipes, [])
  assert.deepEqual(unpiped.sort(), ['a', 'b', 'c'])
})

test('emits exactly one unpipe event per destination', () => {
  const source = new Readable({ read() {} })
  let count = 0
  const dest = discard(() => {
    count += 1
  })
  source.pipe(dest)

  unpipeAll(source)
  unpipeAll(source)

  assert.equal(count, 1)
})

test('is safe when no destinations are attached', () => {
  const source = new Readable({ read() {} })
  assert.doesNotThrow(() => unpipeAll(source))
  assert.deepEqual(source._readableState.pipes, [])
})

test('re-detaches destinations added during teardown', () => {
  const source = new Readable({ read() {} })
  const late = discard()
  let added = false

  const first = discard(() => {
    if (!added) {
      added = true
      source.pipe(late)
    }
  })

  source.pipe(first)
  unpipeAll(source)

  assert.equal(added, true)
  assert.deepEqual(source._readableState.pipes, [])
})

test('can unpipe a PassThrough mid-flow and keep reading locally', () => {
  const source = Readable.from(['one', 'two', 'three'])
  const dest = new PassThrough()
  source.pipe(dest)

  unpipeAll(source)

  assert.deepEqual(source._readableState.pipes, [])
  assert.equal(dest.readableEnded, false)
})

test('throws a TypeError for non-stream input', () => {
  assert.throws(() => unpipeAll(null), TypeError)
  assert.throws(() => unpipeAll({}), TypeError)
})
