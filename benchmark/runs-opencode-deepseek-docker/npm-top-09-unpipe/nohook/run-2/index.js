"use strict";

const http = require("http");
const { Readable } = require("stream");
const unpipe = require("unpipe");

const PORT = process.env.PORT || 3000;

function createSource() {
  let n = 0;
  return new Readable({
    read() {
      if (n >= 10) {
        this.push(null);
        return;
      }
      this.push(`chunk ${++n}\n`);
    },
  });
}

function streamTo(res) {
  const source = createSource();

  const stop = () => {
    unpipe(source);
    if (!res.writableEnded) res.end("\n[unpiped from all destinations]\n");
  };

  source.pipe(res);
  res.on("close", stop);

  return source;
}

const server = http.createServer((req, res) => {
  if (req.url === "/stream") {
    res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
    streamTo(res);
    return;
  }

  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok" }));
    return;
  }

  res.writeHead(404, { "Content-Type": "text/plain" });
  res.end("Not Found\n");
});

if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`server listening on http://localhost:${PORT}`);
  });
}

module.exports = { server, streamTo, createSource };
