import { createServer } from 'node:http'
import { Readable } from 'node:stream'
import { setTimeout as delay } from 'node:timers/promises'
import unpipe from 'unpipe'

export class Broadcaster {
  #source
  #destinations = new Set()

  constructor(source) {
    this.#source = source
  }

  get source() {
    return this.#source
  }

  get size() {
    return this.#destinations.size
  }

  add(destination) {
    if (this.#destinations.has(destination)) return destination

    this.#destinations.add(destination)
    destination.once('close', () => this.remove(destination))
    this.#source.pipe(destination, { end: false })
    return destination
  }

  remove(destination) {
    if (!this.#destinations.delete(destination)) return false
    this.#source.unpipe(destination)
    return true
  }

  unpipeAll() {
    const dropped = this.#destinations.size
    this.#destinations.clear()

    // `unpipe` delegates to Readable#unpipe() when it exists, which detaches
    // every destination and emits 'unpipe' for each one. It also covers legacy
    // pipe-like streams that predate the method.
    unpipe(this.#source)
    this.#source.pause()
    return dropped
  }
}

export function ticker(intervalMs = 1000) {
  let tick = 0
  let destroyed = false
  return new Readable({
    read() {
      delay(intervalMs).then(() => {
        if (destroyed) return
        tick += 1
        this.push(`${JSON.stringify({ tick, at: Date.now() })}\n`)
      })
    },
    destroy(error, callback) {
      destroyed = true
      callback(error)
    },
  })
}

export function createStreamServer({ intervalMs = 1000 } = {}) {
  const broadcaster = new Broadcaster(ticker(intervalMs))
  const { source } = broadcaster

  const server = createServer((req, res) => {
    if (req.method !== 'GET') {
      res.writeHead(405).end()
      return
    }

    if (req.url === '/stop') {
      const unpiped = broadcaster.unpipeAll()
      res.writeHead(200, { 'content-type': 'application/json' })
      res.end(JSON.stringify({ unpiped }))
      return
    }

    if (req.url !== '/') {
      res.writeHead(404).end()
      return
    }

    res.writeHead(200, {
      'content-type': 'application/x-ndjson',
      'cache-control': 'no-cache',
    })
    broadcaster.add(res)
  })

  const shutdown = () => {
    broadcaster.unpipeAll()
    source.destroy()
  }

  return { server, broadcaster, source, shutdown }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const { server, shutdown } = createStreamServer()
  const port = Number(process.env.PORT ?? 3000)

  server.listen(port, () => {
    console.log(`listening on http://localhost:${port}`)
    console.log('GET /      stream ticks from the shared source')
    console.log('GET /stop  reliably unpipe the source from every destination')
  })

  const stop = () => {
    shutdown()
    server.close()
  }
  process.on('SIGINT', stop)
  process.on('SIGTERM', stop)
}
