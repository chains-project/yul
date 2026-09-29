import http from 'node:http'
import { Readable } from 'node:stream'
import { unpipeAll } from './stream-utils.js'

const PORT = Number(process.env.PORT) || 3000

/**
 * A shared source stream that emits one timestamped line per second. Every
 * connected client is piped from this single readable, so it is the stream we
 * must be able to unpipe from all destinations on demand.
 */
function createTicker(intervalMs = 1000) {
  let seq = 0
  let timer = null

  const stream = new Readable({
    read() {
      if (timer) return
      timer = setInterval(() => {
        seq += 1
        stream.push(`event ${seq} ${new Date().toISOString()}\n`)
      }, intervalMs)
      timer.unref?.()
    },
  })

  stream.once('close', () => {
    if (timer) clearInterval(timer)
    timer = null
  })

  return stream
}

const ticker = createTicker()

function json(res, status, body) {
  const payload = JSON.stringify(body)
  res.writeHead(status, {
    'content-type': 'application/json',
    'content-length': Buffer.byteLength(payload),
  })
  res.end(payload)
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host ?? 'localhost'}`)

  if (req.method === 'GET' && url.pathname === '/stream') {
    res.writeHead(200, {
      'content-type': 'text/event-stream',
      'cache-control': 'no-cache',
      connection: 'keep-alive',
    })
    res.write(': connected\n\n')
    ticker.pipe(res)

    // When the client goes away, detach just this destination.
    res.once('close', () => {
      ticker.unpipe(res)
    })
    return
  }

  if (req.method === 'POST' && url.pathname === '/stream/detach') {
    const before = ticker._readableState?.pipes?.length ?? 0
    unpipeAll(ticker)
    const after = ticker._readableState?.pipes?.length ?? 0
    json(res, 200, { detached: before, remaining: after })
    return
  }

  if (req.method === 'GET' && url.pathname === '/health') {
    json(res, 200, { status: 'ok' })
    return
  }

  json(res, 404, { error: 'not found' })
})

server.listen(PORT, () => {
  console.log(`stream-broadcast-server listening on http://localhost:${PORT}`)
})

export { server, ticker, createTicker }
