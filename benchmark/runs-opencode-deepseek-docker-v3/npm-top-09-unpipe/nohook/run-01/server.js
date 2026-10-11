'use strict'

const http = require('http')
const { Readable } = require('stream')
const StreamHub = require('./src/stream-hub')

const PORT = process.env.PORT || 3000

function createTicker() {
  let timer
  return new Readable({
    read() {
      this.push(`tick ${Date.now()}\n`)
      timer = setTimeout(() => this.read(0), 1000)
    },
    destroy(err, callback) {
      clearTimeout(timer)
      callback(err)
    },
  })
}

const server = http.createServer((req, res) => {
  if (req.url !== '/stream') {
    res.writeHead(404, { 'content-type': 'text/plain' })
    res.end('Not Found')
    return
  }

  res.writeHead(200, {
    'content-type': 'text/plain; charset=utf-8',
    'cache-control': 'no-cache',
  })

  const source = createTicker()
  const hub = new StreamHub(source)
  hub.add(res)

  let closed = false
  const cleanup = () => {
    if (closed) return
    closed = true
    hub.removeAll()
    source.destroy()
  }

  req.on('close', cleanup)
  res.on('close', cleanup)
})

if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`listening on http://localhost:${PORT}`)
  })
}

module.exports = server
