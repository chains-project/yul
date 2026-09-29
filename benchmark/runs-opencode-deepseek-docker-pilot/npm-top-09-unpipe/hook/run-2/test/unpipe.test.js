import { test } from 'node:test'
import assert from 'node:assert/strict'
import { Readable, Writable } from 'node:stream'
import { unpipeAll } from '../src/unpipe.js'

function makeSource() {
  return new Readable({ read() {} })
}

function makeSink(name, log) {
  return new Writable({
    write(chunk, _enc, cb) {
      log.push(`${name}:${chunk}`)
      cb()
    },
  })
}

const tick = () => new Promise((resolve) => setImmediate(resolve))

test('detaches every destination', async () => {
  const source = makeSource()
  const log = []
  source.pipe(makeSink('a', log))
  source.pipe(makeSink('b', log))

  const passes = unpipeAll(source)

  assert.equal(passes, 1)
  assert.equal(source._readableState.pipes.length, 0)

  source.push('later')
  source.push(null)
  await tick()
  assert.deepEqual(log, [])
})

test('re-drains a destination attached by an unpipe handler', async () => {
  const source = makeSource()
  const log = []
  const a = makeSink('a', log)
  const late = makeSink('late', log)
  source.pipe(a)
  a.once('unpipe', () => source.pipe(late))

  const passes = unpipeAll(source)

  assert.equal(passes, 2)
  assert.equal(source._readableState.pipes.length, 0)

  source.push('later')
  source.push(null)
  await tick()
  assert.deepEqual(log, [])
})

test('throws instead of hanging when a destination re-pipes forever', () => {
  const source = makeSource()
  const a = makeSink('a', [])
  source.pipe(a)
  a.on('unpipe', () => source.pipe(a))

  assert.throws(() => unpipeAll(source, { maxPasses: 5 }), /kept re-piping/)
})

test('rejects non-readable input', () => {
  assert.throws(() => unpipeAll({}), TypeError)
  assert.throws(() => unpipeAll(null), TypeError)
})
