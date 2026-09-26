const http = require('http')
const { PassThrough } = require('stream')
const unpipe = require('unpipe')

const server = http.createServer((req, res) => {
  const source = new PassThrough()
  const destinations = [res]

  destinations.forEach((dest) => source.pipe(dest))

  req.on('aborted', () => {
    unpipe(source)
  })

  source.end('hello from unpipe-server\n')
})

const port = process.env.PORT || 3000
server.listen(port, () => {
  console.log(`listening on port ${port}`)
})
