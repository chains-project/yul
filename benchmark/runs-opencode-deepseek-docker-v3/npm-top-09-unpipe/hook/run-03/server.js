'use strict'

const http = require('node:http')
const { Readable } = require('node:stream')
const unpipe = require('unpipe')

const PORT = process.env.PORT || 3000

let sequence = 0

function createSource() {
  return new Readable({
    read() {
      sequence += 1
      if (sequence > 100000) {
        this.push(null)
        return
      }
      this.push(`chunk-${sequence}\n`)
    },
  })
}

function detach(source) {
  unpipe(source)
  source.destroy()
}

const server = http.createServer((req, res) => {
  if (req.url !== '/stream') {
    res.writeHead(404, { 'content-type': 'text/plain' })
    res.end('not found\n')
    return
  }

  res.writeHead(200, {
    'content-type': 'text/plain',
    'transfer-encoding': 'chunked',
  })

  const source = createSource()
  source.pipe(res)

  const cleanup = () => detach(source)
  req.on('aborted', cleanup)
  res.on('close', cleanup)
  res.on('error', cleanup)
})

server.listen(PORT, () => {
  console.log(`stream server listening on http://localhost:${PORT}`)
})
