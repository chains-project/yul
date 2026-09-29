'use strict'

const realpath = require('fs.realpath')

function assertPath (filepath) {
  if (typeof filepath !== 'string' || filepath.length === 0) {
    throw new TypeError('filepath must be a non-empty string')
  }
}

function canonicalizeSync (filepath, cache) {
  assertPath(filepath)
  return realpath.realpathSync(filepath, cache)
}

function canonicalize (filepath, cache) {
  assertPath(filepath)

  return new Promise((resolve, reject) => {
    realpath.realpath(filepath, cache, (err, resolved) => {
      if (err) reject(err)
      else resolve(resolved)
    })
  })
}

module.exports = { canonicalize, canonicalizeSync }
