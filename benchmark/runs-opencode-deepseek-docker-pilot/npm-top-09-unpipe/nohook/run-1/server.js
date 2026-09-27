'use strict'

const http = require('node:http')
const { PassThrough, Writable } = require('node:stream')
const unpipe = require('./lib/unpipe')

const MAX_BYTES = 1024 * 1024

function upload (req, res) {
  const counter = new PassThrough()
  const sink = new Writable({ write (chunk, encoding, callback) { callback() } })

  let bytes = 0
  let settled = false

  function finish (status, body) {
    if (settled) {
      return
    }
    settled = true

    unpipe(req)
    req.resume()

    if (res.writableEnded || res.destroyed) {
      return
    }

    res.writeHead(status, { 'content-type': 'text/plain' })
    res.end(body)
  }

  counter.on('data', (chunk) => {
    bytes += chunk.length

    if (bytes > MAX_BYTES) {
      finish(413, 'payload too large\n')
    }
  })

  counter.on('error', () => finish(400, 'bad request\n'))
  sink.on('error', () => {})

  req.pipe(counter)
  req.pipe(sink)

  req.once('aborted', () => {
    settled = true
    unpipe(req)
  })

  req.once('error', () => finish(400, 'bad request\n'))

  req.once('end', () => finish(201, `received ${bytes} bytes\n`))
}

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/upload') {
    return upload(req, res)
  }

  res.writeHead(404, { 'content-type': 'text/plain' })
  res.end('not found\n')
})

if (require.main === module) {
  server.listen(process.env.PORT || 3000, () => {
    console.log(`listening on http://localhost:${server.address().port}`)
  })
}

module.exports = { server, upload, MAX_BYTES }
