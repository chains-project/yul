import http from "node:http";
import { fileURLToPath } from "node:url";
import { Writable } from "node:stream";
import { unpipeAll } from "./unpipe-all.js";

export function createSink() {
  let bytes = 0;
  let chunks = 0;

  const stream = new Writable({
    write(chunk, _encoding, callback) {
      bytes += chunk.length;
      chunks += 1;
      callback();
    },
  });

  return {
    stream,
    get bytes() {
      return bytes;
    },
    get chunks() {
      return chunks;
    },
  };
}

export function createServer() {
  return http.createServer((req, res) => {
    if (req.method === "GET" && req.url === "/health") {
      res.writeHead(200, { "content-type": "text/plain" });
      res.end("ok");
      return;
    }

    if (req.method !== "POST") {
      res.writeHead(405, { "content-type": "text/plain" });
      res.end("method not allowed");
      return;
    }

    const sinks = [createSink(), createSink()];
    for (const sink of sinks) {
      req.pipe(sink.stream);
    }

    let settled = false;

    const detach = () => {
      if (settled) return;
      settled = true;
      unpipeAll(req);
      for (const sink of sinks) {
        sink.stream.destroy();
      }
    };

    req.once("aborted", detach);
    req.once("error", detach);
    res.once("close", detach);

    req.once("end", () => {
      if (settled) return;
      settled = true;
      unpipeAll(req);
      const payload = JSON.stringify({
        bytes: sinks[0].bytes,
        chunks: sinks[0].chunks,
      });
      res.writeHead(200, {
        "content-type": "application/json",
        "content-length": Buffer.byteLength(payload),
      });
      res.end(payload);
    });
  });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT) || 3000;
  const server = createServer();
  server.listen(port, () => {
    console.log(`listening on http://localhost:${port}`);
  });
}
