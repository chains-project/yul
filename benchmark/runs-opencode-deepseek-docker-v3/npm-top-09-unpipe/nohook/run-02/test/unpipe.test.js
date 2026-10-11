import { test } from 'node:test'
import assert from 'node:assert/strict'
import { PassThrough } from 'node:stream'
import { trackDestinations, unpipeAll } from '../src/unpipe.js'

function collect(stream) {
  const chunks = []
  stream.on('data', (chunk) => chunks.push(chunk.toString()))
  return chunks
}

test('tracks every destination of a readable', () => {
  const source = new PassThrough()
  const tracker = trackDestinations(source)
  const a = new PassThrough()
  const b = new PassThrough()

  source.pipe(a)
  source.pipe(b)

  assert.equal(tracker.size, 2)
  assert.deepEqual(new Set(tracker.destinations), new Set([a, b]))
})

test('unpipeAll detaches every destination', () => {
  const source = new PassThrough()
  const tracker = trackDestinations(source)
  const a = new PassThrough()
  const b = new PassThrough()
  source.pipe(a)
  source.pipe(b)

  const aSeen = collect(a)
  const bSeen = collect(b)

  tracker.unpipeAll()

  assert.equal(tracker.size, 0)

  source.write('after-unpipe')

  assert.deepEqual(aSeen, [])
  assert.deepEqual(bSeen, [])
})

test('unpipeAll works on an untracked stream', () => {
  const source = new PassThrough()
  const a = new PassThrough()
  const b = new PassThrough()
  source.pipe(a)
  source.pipe(b)

  const aSeen = collect(a)
  const bSeen = collect(b)

  assert.equal(unpipeAll(source), source)

  source.write('after-unpipe')

  assert.deepEqual(aSeen, [])
  assert.deepEqual(bSeen, [])
})

test('unpipeAll is idempotent and returns the readable', () => {
  const source = new PassThrough()
  const tracker = trackDestinations(source)
  source.pipe(new PassThrough())

  assert.equal(tracker.unpipeAll(), source)
  assert.equal(tracker.unpipeAll(), source)
  assert.equal(tracker.size, 0)
})

test('destinations removed after a destination error', async () => {
  const source = new PassThrough()
  const tracker = trackDestinations(source)
  const destination = new PassThrough()
  source.pipe(destination)

  assert.equal(tracker.size, 1)

  const closed = new Promise((resolve) => destination.once('close', resolve))
  destination.destroy(new Error('boom'))
  await closed

  assert.equal(tracker.size, 0)
})

test('stopTracking restores the original pipe', () => {
  const source = new PassThrough()
  const originalPipe = source.pipe
  const tracker = trackDestinations(source)

  tracker.stopTracking()

  assert.equal(source.pipe, originalPipe)
  assert.equal(trackDestinations(source).size, 0)
})
