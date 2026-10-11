import { test } from 'node:test'
import assert from 'node:assert/strict'
import { Readable, Writable } from 'node:stream'
import { Broadcaster, ticker } from '../server.js'

function collector() {
  const chunks = []
  const writable = new Writable({
    write(chunk, _encoding, callback) {
      chunks.push(chunk.toString())
      callback()
    },
  })
  return { writable, chunks }
}

test('unpipeAll detaches the source from every destination', async () => {
  const source = ticker(5)
  const broadcaster = new Broadcaster(source)
  const a = collector()
  const b = collector()
  const c = collector()

  broadcaster.add(a.writable)
  broadcaster.add(b.writable)
  broadcaster.add(c.writable)

  assert.equal(source.listenerCount('data'), 3)
  assert.equal(broadcaster.size, 3)

  const dropped = broadcaster.unpipeAll()

  assert.equal(dropped, 3)
  assert.equal(broadcaster.size, 0)
  assert.equal(source.listenerCount('data'), 0)
  assert.equal(source.listenerCount('unpipe'), 0)
  assert.equal(source.isPaused(), true)

  const seen = a.chunks.length + b.chunks.length + c.chunks.length
  await new Promise((resolve) => setTimeout(resolve, 30))
  assert.equal(a.chunks.length + b.chunks.length + c.chunks.length, seen)

  source.destroy()
})

test('remove detaches a single destination only', () => {
  const source = new Readable({ read() {} })
  const broadcaster = new Broadcaster(source)
  const a = collector()
  const b = collector()

  broadcaster.add(a.writable)
  broadcaster.add(b.writable)

  assert.equal(broadcaster.remove(a.writable), true)
  assert.equal(broadcaster.remove(a.writable), false)
  assert.equal(broadcaster.size, 1)
  assert.equal(source.listenerCount('data'), 1)

  broadcaster.unpipeAll()
  assert.equal(source.listenerCount('data'), 0)
  assert.equal(broadcaster.size, 0)
  source.destroy()
})
