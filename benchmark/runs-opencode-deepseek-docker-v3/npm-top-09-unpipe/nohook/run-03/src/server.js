import http from "node:http"
import { PassThrough, Readable } from "node:stream"
import { pipe, unpipeAll } from "./unpipe.js"

const PORT = Number(process.env.PORT ?? 3000)

function createSource() {
  let index = 0
  return new Readable({
    read() {
      index += 1
      if (index <= 5) {
        this.push(`chunk ${index}\n`)
      } else {
        this.push(null)
      }
    },
  })
}

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "content-type": "application/json" })
    res.end(JSON.stringify({ status: "ok" }))
    return
  }

  const source = createSource()

  const audit = new PassThrough()
  audit.on("data", (chunk) => process.stdout.write(`[audit] ${chunk}`))

  pipe(source, res)
  pipe(source, audit)

  res.on("close", () => {
    unpipeAll(source)
    audit.destroy()
  })
})

server.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`)
})

export { server, createSource }
