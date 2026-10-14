'use strict'

const { test } = require('node:test')
const assert = require('node:assert')
const { createServer } = require('../src/server')

test('server echoes POST /echo and answers health checks', async (t) => {
  const server = createServer().listen(0)
  t.after(() => server.close())
  await new Promise((resolve) => server.once('listening', resolve))
  const base = `http://localhost:${server.address().port}`

  const health = await fetch(base)
  assert.deepStrictEqual(await health.json(), { status: 'ok' })

  const echo = await fetch(`${base}/echo`, { method: 'POST', body: 'ping' })
  assert.strictEqual(await echo.text(), 'ping')
})
