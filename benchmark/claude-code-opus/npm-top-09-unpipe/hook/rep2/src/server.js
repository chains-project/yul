'use strict'

const crypto = require('node:crypto')
const http = require('node:http')
const { Writable } = require('node:stream')
const { finished } = require('node:stream/promises')
const unpipe = require('./unpipe')

const DEFAULT_MAX_BODY_BYTES = 1024 * 1024

function createServer ({ maxBodyBytes = DEFAULT_MAX_BODY_BYTES } = {}) {
  return http.createServer((req, res) => {
    if (req.method === 'GET' && req.url === '/health') {
      sendJson(res, 200, { status: 'ok' })
      return
    }

    if (req.method === 'POST' && req.url === '/digest') {
      digest(req, res, maxBodyBytes)
      return
    }

    sendJson(res, 404, { error: 'not found' })
  })
}

// Pipes the request body into two destinations: a SHA-256 hash and a byte
// counter. If the body exceeds the limit, the request is unpiped from all
// destinations at once and the remainder is drained and discarded.
function digest (req, res, maxBodyBytes) {
  const hash = crypto.createHash('sha256')
  let bytes = 0
  let rejected = false

  const counter = new Writable({
    write (chunk, encoding, callback) {
      bytes += chunk.length
      if (bytes > maxBodyBytes && !rejected) {
        rejected = true
        unpipe(req)
        req.resume()
        res.setHeader('connection', 'close')
        sendJson(res, 413, { error: 'payload too large', limit: maxBodyBytes })
      }
      callback()
    }
  })

  let sha256 = ''
  hash.setEncoding('hex')
  hash.on('data', (hex) => { sha256 += hex })

  Promise.all([finished(hash), finished(counter)]).then(() => {
    if (rejected) return
    sendJson(res, 200, { bytes, sha256 })
  }, () => res.destroy())
  req.on('error', () => res.destroy())

  req.pipe(hash)
  req.pipe(counter)
}

function sendJson (res, status, body) {
  const payload = JSON.stringify(body)
  res.writeHead(status, {
    'content-type': 'application/json',
    'content-length': Buffer.byteLength(payload)
  })
  res.end(payload)
}

module.exports = { createServer }

if (require.main === module) {
  const port = Number(process.env.PORT) || 3000
  createServer().listen(port, () => {
    console.log(`listening on http://localhost:${port}`)
  })
}
