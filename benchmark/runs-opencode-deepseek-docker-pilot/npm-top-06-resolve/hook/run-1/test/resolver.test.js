import test from 'node:test'
import assert from 'node:assert/strict'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { dirname, join } from 'node:path'
import { createResolver, resolve } from '../src/index.js'

const here = dirname(fileURLToPath(import.meta.url))
const app = join(here, 'fixtures/app/index.js')

test('resolves Node builtins', () => {
  const r = createResolver(app)
  assert.equal(r.resolve('fs'), 'fs')
  assert.equal(r.resolve('node:path'), 'node:path')
})

test('resolves a relative path against the anchor', () => {
  const r = createResolver(app)
  assert.equal(r.resolve('./local.js'), join(here, 'fixtures/app/local.js'))
})

test('resolves a package main from node_modules', () => {
  const r = createResolver(app)
  assert.equal(
    r.resolve('dep'),
    join(here, 'fixtures/app/node_modules/dep/lib/main.js'),
  )
})

test('honors the "require" condition in package exports', () => {
  const r = createResolver(app)
  assert.equal(
    r.resolve('esm-dep'),
    join(here, 'fixtures/app/node_modules/esm-dep/cjs.js'),
  )
})

test('resolve() accepts a file URL anchor', () => {
  assert.equal(
    resolve('dep', pathToFileURL(app)),
    join(here, 'fixtures/app/node_modules/dep/lib/main.js'),
  )
})
