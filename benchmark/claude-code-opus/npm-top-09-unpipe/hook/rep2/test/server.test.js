'use strict'

const assert = require('node:assert/strict')
const crypto = require('node:crypto')
const { after, before, test } = require('node:test')
const { createServer } = require('../src/server')

let server
let baseUrl

before(async () => {
  server = createServer({ maxBodyBytes: 1024 })
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve))
  baseUrl = `http://127.0.0.1:${server.address().port}`
})

after(() => new Promise((resolve) => server.close(resolve)))

test('GET /health', async () => {
  const res = await fetch(`${baseUrl}/health`)
  assert.equal(res.status, 200)
  assert.deepEqual(await res.json(), { status: 'ok' })
})

test('POST /digest hashes a body under the limit', async () => {
  const body = 'hello world'
  const res = await fetch(`${baseUrl}/digest`, { method: 'POST', body })
  assert.equal(res.status, 200)
  assert.deepEqual(await res.json(), {
    bytes: body.length,
    sha256: crypto.createHash('sha256').update(body).digest('hex')
  })
})

test('POST /digest unpipes and rejects a body over the limit', async () => {
  const res = await fetch(`${baseUrl}/digest`, {
    method: 'POST',
    body: Buffer.alloc(64 * 1024, 'a')
  })
  assert.equal(res.status, 413)
  assert.deepEqual(await res.json(), { error: 'payload too large', limit: 1024 })
})

test('unknown routes return 404', async () => {
  const res = await fetch(`${baseUrl}/nope`)
  assert.equal(res.status, 404)
})
