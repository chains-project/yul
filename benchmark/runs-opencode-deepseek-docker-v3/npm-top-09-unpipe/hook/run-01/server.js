import http from "node:http";
import { PassThrough, Readable } from "node:stream";
import { pipeTo, unpipeAll } from "./src/unpipe-all.js";

const PORT = Number(process.env.PORT ?? 3000);

function createSource() {
  let chunk = 0;
  return new Readable({
    read() {
      if (chunk >= 100) {
        this.push(null);
        return;
      }
      this.push(`chunk-${++chunk}\n`);
    },
  });
}

const server = http.createServer((req, res) => {
  if (req.url !== "/stream") {
    res.writeHead(404, { "content-type": "text/plain" }).end("not found\n");
    return;
  }

  const source = createSource();
  const sink = new PassThrough();
  sink.on("data", () => {});

  pipeTo(source, res);
  pipeTo(source, sink);

  const detachAll = () => unpipeAll(source);

  res.on("close", detachAll);
  res.on("error", detachAll);
  req.on("aborted", detachAll);
  source.on("end", detachAll);
  source.on("error", detachAll);

  res.writeHead(200, { "content-type": "text/plain" });
});

server.listen(PORT, () => {
  console.log(`listening on http://localhost:${PORT}`);
});

export { server };
