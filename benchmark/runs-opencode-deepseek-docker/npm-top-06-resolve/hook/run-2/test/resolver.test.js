import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import test from 'node:test'

import { resolve, isBuiltin, ResolveError } from '../src/index.js'

let root

function write(relative, contents = '') {
  const target = path.join(root, relative)
  fs.mkdirSync(path.dirname(target), { recursive: true })
  fs.writeFileSync(target, contents)
}

function real(relative) {
  return fs.realpathSync(path.join(root, relative))
}

test.before(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), 'resolver-'))

  write('package.json', JSON.stringify({
    name: 'self-pkg',
    exports: { '.': './lib/self.js', './util': './lib/util.js' },
    imports: { '#internal': './lib/internal.js' },
  }))
  write('lib/self.js')
  write('lib/util.js')
  write('lib/internal.js')
  write('lib/index.js')
  write('lib/nested/index.js')
  write('lib/nested/package.json', JSON.stringify({ main: 'missing-main.js' }))

  write('node_modules/abc/package.json', JSON.stringify({ main: 'lib/main.js' }))
  write('node_modules/abc/lib/main.js')

  write('node_modules/dce/package.json', JSON.stringify({
    exports: {
      '.': './dist/index.js',
      './feature/*': './dist/feature/*.js',
    },
  }))
  write('node_modules/dce/dist/index.js')
  write('node_modules/dce/dist/feature/one.js')

  write('node_modules/cond/package.json', JSON.stringify({
    exports: { '.': { import: './esm.js', require: './cjs.js', default: './cjs.js' } },
  }))
  write('node_modules/cond/esm.js')
  write('node_modules/cond/cjs.js')

  write('node_modules/@scope/pkg/index.js')
})

test.after(() => {
  fs.rmSync(root, { recursive: true, force: true })
})

test('builtins are returned by name', () => {
  assert.equal(resolve('fs'), 'fs')
  assert.equal(resolve('node:path'), 'node:path')
  assert.equal(isBuiltin('fs'), true)
})

test('relative specifiers resolve to a file', () => {
  const from = path.join(root, 'app.js')
  assert.equal(resolve('./lib/self', { from }), real('lib/self.js'))
  assert.equal(resolve('./lib', { from }), real('lib/index.js'))
})

test('absolute specifiers resolve', () => {
  const from = path.join(root, 'app.js')
  assert.equal(resolve(path.join(root, 'lib/util'), { from }), real('lib/util.js'))
})

test('bare specifier resolves through package.json main', () => {
  const from = path.join(root, 'app.js')
  assert.equal(resolve('abc', { from }), real('node_modules/abc/lib/main.js'))
})

test('scoped packages resolve', () => {
  const from = path.join(root, 'app.js')
  assert.equal(resolve('@scope/pkg', { from }), real('node_modules/@scope/pkg/index.js'))
})

test('package exports map resolves subpaths and patterns', () => {
  const from = path.join(root, 'app.js')
  assert.equal(resolve('dce', { from }), real('node_modules/dce/dist/index.js'))
  assert.equal(resolve('dce/feature/one', { from }), real('node_modules/dce/dist/feature/one.js'))
})

test('conditional exports honour the require condition', () => {
  const from = path.join(root, 'app.js')
  assert.equal(resolve('cond', { from }), real('node_modules/cond/cjs.js'))
  assert.equal(
    resolve('cond', { from, conditions: ['node', 'import'] }),
    real('node_modules/cond/esm.js'),
  )
})

test('self-referencing a package by name', () => {
  const from = path.join(root, 'app.js')
  assert.equal(resolve('self-pkg', { from }), real('lib/self.js'))
  assert.equal(resolve('self-pkg/util', { from }), real('lib/util.js'))
})

test('package imports (# specifiers)', () => {
  const from = path.join(root, 'app.js')
  assert.equal(resolve('#internal', { from }), real('lib/internal.js'))
})

test('falls back to index when package.json main is missing', () => {
  const from = path.join(root, 'app.js')
  assert.equal(resolve('./lib/nested', { from }), real('lib/nested/index.js'))
})

test('throws ResolveError for unresolvable specifiers', () => {
  const from = path.join(root, 'app.js')
  assert.throws(
    () => resolve('does-not-exist', { from }),
    (error) => error instanceof ResolveError && error.code === 'MODULE_NOT_FOUND',
  )
})
