import { test } from 'node:test'
import assert from 'node:assert/strict'
import { start } from '../src/server.js'

const TIMEOUT = Symbol('timeout')

async function connect(url) {
  const res = await fetch(`${url}/stream`)
  const reader = res.body.getReader()
  return {
    res,
    async nextChunk(ms = 1000) {
      const timer = new Promise((resolve) => setTimeout(() => resolve(TIMEOUT), ms))
      const chunk = reader.read().then(({ value }) =>
        value ? new TextDecoder().decode(value) : null,
      )
      return Promise.race([chunk, timer])
    },
    close() {
      return reader.cancel().catch(() => {})
    },
  }
}

async function waitFor(predicate, ms = 1000) {
  const deadline = Date.now() + ms
  while (Date.now() < deadline) {
    if (predicate()) return
    await new Promise((resolve) => setTimeout(resolve, 10))
  }
  throw new Error('timed out waiting for condition')
}

test('POST /detach unpipes the broadcast from every client', async (t) => {
  const app = await start(0)
  const url = `http://127.0.0.1:${app.port}`

  const a = await connect(url)
  const b = await connect(url)
  await waitFor(() => app.destinations.size === 2)

  t.after(async () => {
    await Promise.all([a.close(), b.close()])
    app.server.closeAllConnections?.()
    await new Promise((resolve) => app.server.close(resolve))
  })

  await fetch(`${url}/publish`, { method: 'POST', body: 'hello' })
  assert.equal(await a.nextChunk(), 'hello')
  assert.equal(await b.nextChunk(), 'hello')

  const detached = await (await fetch(`${url}/detach`, { method: 'POST' })).json()
  assert.equal(detached.detached, true)
  assert.ok(detached.passes >= 1)
  assert.equal(app.destinations.size, 0)

  await fetch(`${url}/publish`, { method: 'POST', body: 'after' })
  assert.equal(await a.nextChunk(150), TIMEOUT)
  assert.equal(await b.nextChunk(150), TIMEOUT)
})
