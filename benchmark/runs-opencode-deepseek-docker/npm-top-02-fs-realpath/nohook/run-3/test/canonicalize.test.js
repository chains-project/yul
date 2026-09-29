'use strict'

const assert = require('node:assert')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const test = require('node:test')

const { canonicalize, canonicalizeSync } = require('..')

function fixture () {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'canonicalize-'))
  const realDir = path.join(dir, 'real')
  fs.mkdirSync(realDir)
  const file = path.join(realDir, 'file.txt')
  fs.writeFileSync(file, 'hello')

  const link = path.join(dir, 'link')
  fs.symlinkSync(realDir, link)
  const chained = path.join(dir, 'chained')
  fs.symlinkSync(link, chained)

  return { dir, realDir, file, link, chained }
}

test('resolves a symlinked directory to its real path', (t) => {
  const f = fixture()
  t.after(() => fs.rmSync(f.dir, { recursive: true, force: true }))

  assert.strictEqual(canonicalizeSync(f.link), fs.realpathSync(f.realDir))
})

test('follows a chain of symlinks', (t) => {
  const f = fixture()
  t.after(() => fs.rmSync(f.dir, { recursive: true, force: true }))

  assert.strictEqual(canonicalizeSync(f.chained), fs.realpathSync(f.realDir))
})

test('resolves a file reached through a symlink', (t) => {
  const f = fixture()
  t.after(() => fs.rmSync(f.dir, { recursive: true, force: true }))

  const viaLink = path.join(f.link, 'file.txt')
  assert.strictEqual(canonicalizeSync(viaLink), fs.realpathSync(f.file))
})

test('async and sync agree', async (t) => {
  const f = fixture()
  t.after(() => fs.rmSync(f.dir, { recursive: true, force: true }))

  assert.strictEqual(await canonicalize(f.chained), canonicalizeSync(f.chained))
})

test('an already-canonical path is unchanged', (t) => {
  const f = fixture()
  t.after(() => fs.rmSync(f.dir, { recursive: true, force: true }))

  const real = canonicalizeSync(f.realDir)
  assert.strictEqual(canonicalizeSync(real), real)
})

test('rejects an empty path', () => {
  assert.throws(() => canonicalizeSync(''), TypeError)
  assert.throws(() => canonicalize(''), TypeError)
})
