import test from "node:test"
import assert from "node:assert/strict"
import { Readable, Writable } from "node:stream"
import { pipe, unpipeAll, destinationsOf } from "../src/unpipe.js"

function source() {
  let index = 0
  return new Readable({
    read() {
      index += 1
      if (index <= 3) {
        this.push(`chunk ${index}\n`)
      } else {
        this.push(null)
      }
    },
  })
}

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

test("unpipeAll detaches every destination", () => {
  const readable = source()
  const a = collector()
  const b = collector()

  pipe(readable, a)
  pipe(readable, b)

  assert.equal(destinationsOf(readable).length, 2)

  unpipeAll(readable)

  assert.deepEqual(destinationsOf(readable), [])
  assert.equal(readable._readableState.pipes.length, 0)
})

test("no data reaches destinations unpiped before flow", async () => {
  const readable = source()
  const a = collector()
  const b = collector()

  pipe(readable, a)
  pipe(readable, b)
  unpipeAll(readable)

  readable.resume()
  await new Promise((resolve) => readable.on("end", resolve))

  assert.deepEqual(a.chunks, [])
  assert.deepEqual(b.chunks, [])
})

test("unpipeAll is idempotent", () => {
  const readable = source()
  pipe(readable, collector())

  assert.doesNotThrow(() => {
    unpipeAll(readable)
    unpipeAll(readable)
  })
  assert.deepEqual(destinationsOf(readable), [])
})
