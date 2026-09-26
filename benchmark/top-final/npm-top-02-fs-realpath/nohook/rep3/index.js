const { realpath, realpathSync } = require('fs.realpath')

function resolveRealPath(filePath, callback) {
  realpath(filePath, (err, resolvedPath) => {
    if (err) return callback(err)
    callback(null, resolvedPath)
  })
}

function resolveRealPathSync(filePath) {
  return realpathSync(filePath)
}

if (require.main === module) {
  const target = process.argv[2]
  if (!target) {
    console.error('Usage: node index.js <path>')
    process.exit(1)
  }
  resolveRealPath(target, (err, resolvedPath) => {
    if (err) {
      console.error(err.message)
      process.exit(1)
    }
    console.log(resolvedPath)
  })
}

module.exports = { resolveRealPath, resolveRealPathSync }
