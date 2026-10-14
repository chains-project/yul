'use strict'

const http = require('http')
const unpipe = require('./unpipe')

function createServer () {
  return http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/echo') {
      req.pipe(res)

      // If the client goes away mid-request, detach the request body from
      // every destination so nothing keeps writing into a dead response.
      res.on('close', () => {
        if (!res.writableFinished) unpipe(req)
      })
      return
    }

    res.writeHead(200, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({ status: 'ok' }))
  })
}

if (require.main === module) {
  const port = Number(process.env.PORT) || 3000
  createServer().listen(port, () => {
    console.log(`Listening on http://localhost:${port}`)
  })
}

module.exports = { createServer }
