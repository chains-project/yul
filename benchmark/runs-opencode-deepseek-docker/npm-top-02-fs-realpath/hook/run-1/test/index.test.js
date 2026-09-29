'use strict'

const assert = require('assert')
const fs = require('fs')
const os = require('os')
const path = require('path')
const resolveRealPath = require('../index.js')

function canonical(p) {
  return typeof fs.realpathSync.native === 'function'
    ? fs.realpathSync.native(p)
    : fs.realpathSync(p)
}

function removeDir(dir) {
  if (typeof fs.rmSync === 'function') {
    fs.rmSync(dir, { recursive: true, force: true })
  } else {
    fs.rmdirSync(dir, { recursive: true })
  }
}

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'resolve-real-path-'))

try {
  const realDir = path.join(tmp, 'real')
  fs.mkdirSync(path.join(realDir, 'nested'), { recursive: true })
  const link = path.join(tmp, 'link')
  fs.symlinkSync(realDir, link, 'dir')

  assert.strictEqual(resolveRealPath(link), canonical(realDir))
  assert.strictEqual(
    resolveRealPath(path.join(link, 'nested')),
    canonical(path.join(realDir, 'nested'))
  )

  const dirA = path.join(tmp, 'a')
  const dirB = path.join(tmp, 'b')
  fs.mkdirSync(path.join(dirA, 'real'), { recursive: true })
  fs.mkdirSync(path.join(dirA, 'sibling'), { recursive: true })
  fs.mkdirSync(dirB)
  const linkB = path.join(dirB, 'link')
  fs.symlinkSync(path.join(dirA, 'real'), linkB, 'dir')

  assert.strictEqual(
    resolveRealPath(linkB + path.sep + '..' + path.sep + 'sibling'),
    canonical(path.join(dirA, 'sibling'))
  )

  const relative = path.relative(process.cwd(), link)
  assert.strictEqual(resolveRealPath(relative), canonical(realDir))

  console.log('ok')
} finally {
  removeDir(tmp)
}
