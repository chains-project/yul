import http from 'node:http'
import { PassThrough } from 'node:stream'
import { pathToFileURL } from 'node:url'
import { unpipeAll } from './unpipe.js'

/**
 * A tiny fan-out server. One shared readable stream (`broadcast`) is piped to
 * every connected `/stream` client. `detachAll()` reliably unpipes the stream
 * from all of them at once (used by `POST /detach` and on shutdown).
 */
export function createApp() {
  const broadcast = new PassThrough()
  const destinations = new Set()

  function addDestination(res) {
    destinations.add(res)
    broadcast.pipe(res, { end: false })
    res.on('close', () => {
      destinations.delete(res)
      broadcast.unpipe(res)
    })
    return res
  }

  function detachAll() {
    const passes = unpipeAll(broadcast)
    destinations.clear()
    return passes
  }

  const server = http.createServer(async (req, res) => {
    const { pathname } = new URL(req.url, 'http://localhost')

    if (req.method === 'GET' && pathname === '/health') {
      return json(res, 200, { destinations: destinations.size })
    }

    if (req.method === 'GET' && pathname === '/stream') {
      res.writeHead(200, {
        'content-type': 'text/plain; charset=utf-8',
        'cache-control': 'no-cache',
        connection: 'keep-alive',
      })
      res.flushHeaders()
      addDestination(res)
      return
    }

    if (req.method === 'POST' && pathname === '/publish') {
      const chunks = []
      for await (const chunk of req) chunks.push(chunk)
      broadcast.write(Buffer.concat(chunks))
      return json(res, 202, {
        published: true,
        destinations: destinations.size,
      })
    }

    if (req.method === 'POST' && pathname === '/detach') {
      const passes = detachAll()
      return json(res, 200, { detached: true, passes })
    }

    return json(res, 404, { error: 'not found' })
  })

  server.on('close', () => detachAll())

  return { server, broadcast, destinations, detachAll }
}

function json(res, status, body) {
  res.writeHead(status, { 'content-type': 'application/json' })
  res.end(JSON.stringify(body))
}

/**
 * Start the server on an ephemeral port (or `port` if given) for tests.
 */
export function start(port = 0) {
  const app = createApp()
  return new Promise((resolve) => {
    app.server.listen(port, () => {
      resolve({ ...app, port: app.server.address().port })
    })
  })
}

const isMain =
  process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href

if (isMain) {
  const port = Number(process.env.PORT) || 3000
  const app = createApp()

  app.server.listen(port, () => {
    console.log(`listening on http://localhost:${port}`)
  })

  const shutdown = () => {
    app.detachAll()
    app.server.closeAllConnections?.()
    app.server.close(() => process.exit(0))
  }

  process.on('SIGINT', shutdown)
  process.on('SIGTERM', shutdown)
}
