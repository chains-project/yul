'use strict'

const fs = require('fs')

function resolveRealPath(inputPath) {
  if (typeof fs.realpathSync.native === 'function') {
    return fs.realpathSync.native(inputPath)
  }
  return fs.realpathSync(inputPath)
}

module.exports = resolveRealPath
module.exports.resolveRealPath = resolveRealPath
