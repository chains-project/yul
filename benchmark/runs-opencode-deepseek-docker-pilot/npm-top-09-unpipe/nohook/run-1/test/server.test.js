'use strict'

const test = require('node:test')
const assert = require('node:assert/strict')
const http = require('node:http')

const { server, MAX_BYTES } = require('../server')

let port

test.before(async () => {
  await new Promise((resolve) => server.listen(0, resolve))
  port = server.address().port
})

test.after(() => server.close())

function post (body) {
  return new Promise((resolve, reject) => {
    const req = http.request(
      { host: '127.0.0.1', port, method: 'POST', path: '/upload' },
      (res) => {
        const chunks = []
        res.on('data', (chunk) => chunks.push(chunk))
        res.on('end', () =>
          resolve({ status: res.statusCode, body: Buffer.concat(chunks).toString() })
        )
      }
    )
    req.on('error', reject)
    req.end(body)
  })
}

test('accepts an upload and reports the byte count', async () => {
  const res = await post('hello world')

  assert.equal(res.status, 201)
  assert.equal(res.body, 'received 11 bytes\n')
})

test('unpipes from all destinations and rejects oversized payloads', async () => {
  const res = await post(Buffer.alloc(MAX_BYTES + 1, 0x61))

  assert.equal(res.status, 413)
  assert.equal(res.body, 'payload too large\n')
})
