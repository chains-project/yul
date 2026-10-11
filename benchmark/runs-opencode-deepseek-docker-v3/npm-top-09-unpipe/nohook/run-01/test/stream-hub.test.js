'use strict'

const test = require('node:test')
const assert = require('node:assert')
const { PassThrough, Writable } = require('stream')

const StreamHub = require('../src/stream-hub')

const tick = () => new Promise((resolve) => setImmediate(resolve))

function collector() {
  const chunks = []
  const writable = new Writable({
    write(chunk, _encoding, callback) {
      chunks.push(chunk.toString())
      callback()
    },
  })
  writable.chunks = chunks
  return writable
}

test('removeAll unpipes every tracked destination', async () => {
  const source = new PassThrough()
  const hub = new StreamHub(source)
  const a = collector()
  const b = collector()
  hub.add(a)
  hub.add(b)

  hub.removeAll()
  source.write('after')
  await tick()

  assert.deepStrictEqual(a.chunks, [])
  assert.deepStrictEqual(b.chunks, [])
  assert.strictEqual(hub.destinations.size, 0)
})

test('removeAll unpipes destinations the hub never tracked', async () => {
  const source = new PassThrough()
  const hub = new StreamHub(source)
  const tracked = collector()
  const rogue = collector()
  hub.add(tracked)
  source.pipe(rogue)

  hub.removeAll()
  source.write('after')
  await tick()

  assert.deepStrictEqual(tracked.chunks, [])
  assert.deepStrictEqual(rogue.chunks, [])
})

test('remove drops a single destination and keeps the rest', async () => {
  const source = new PassThrough()
  const hub = new StreamHub(source)
  const a = collector()
  const b = collector()
  hub.add(a)
  hub.add(b)

  hub.remove(a)
  source.write('after')
  await tick()

  assert.deepStrictEqual(a.chunks, [])
  assert.deepStrictEqual(b.chunks, ['after'])
})
