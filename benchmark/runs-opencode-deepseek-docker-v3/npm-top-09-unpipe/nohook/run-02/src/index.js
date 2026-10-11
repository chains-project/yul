import http from 'node:http'
import { Readable } from 'node:stream'
import { trackDestinations } from './unpipe.js'

const PORT = Number(process.env.PORT ?? 3000)
const TICK_MS = Number(process.env.TICK_MS ?? 1000)

let seq = 0

const ticks = new Readable({
  read() {
    if (this._timer) return
    this._timer = setInterval(() => {
      seq += 1
      this.push(`data: ${JSON.stringify({ seq, time: new Date().toISOString() })}\n\n`)
    }, TICK_MS)
  },
  destroy(error, callback) {
    clearInterval(this._timer)
    callback(error)
  },
})

const connections = trackDestinations(ticks)

const server = http.createServer((req, res) => {
  switch (req.url) {
    case '/health':
      res.writeHead(200, { 'content-type': 'application/json' })
      res.end(JSON.stringify({ ok: true, destinations: connections.size }))
      return

    case '/events':
      res.writeHead(200, {
        'content-type': 'text/event-stream',
        'cache-control': 'no-cache',
        connection: 'keep-alive',
      })
      ticks.pipe(res)
      req.on('close', () => ticks.unpipe(res))
      return

    case '/disconnect-all': {
      const detached = connections.size
      connections.unpipeAll()
      res.writeHead(200, { 'content-type': 'application/json' })
      res.end(JSON.stringify({ ok: true, detached }))
      return
    }

    default:
      res.writeHead(404, { 'content-type': 'text/plain' })
      res.end('not found')
  }
})

server.listen(PORT, () => {
  console.log(`server listening on http://localhost:${PORT}`)
})

export { server, ticks, connections }
