import http from 'node:http';
import { Readable } from 'node:stream';
import { pathToFileURL } from 'node:url';
import { unpipeAll } from './unpipe.js';

/** Endless source that emits a timestamped line every 100ms. */
function createTicker() {
  let timer;
  return new Readable({
    read() {
      if (timer) return;
      timer = setInterval(() => {
        this.push(`${new Date().toISOString()}\n`);
      }, 100);
    },
    destroy(err, cb) {
      clearInterval(timer);
      cb(err);
    },
  });
}

export function createServer() {
  return http.createServer((req, res) => {
    if (req.method === 'GET' && req.url === '/health') {
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ status: 'ok' }));
      return;
    }

    if (req.method === 'GET' && req.url === '/stream') {
      const source = createTicker();
      res.writeHead(200, { 'content-type': 'text/plain; charset=utf-8' });
      source.pipe(res);

      // When the client goes away, detach the source from every destination
      // before destroying it so nothing writes to a closed socket.
      res.on('close', () => {
        unpipeAll(source);
        source.destroy();
      });
      return;
    }

    res.writeHead(404, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ error: 'not found' }));
  });
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT) || 3000;
  const server = createServer();
  server.listen(port, () => {
    console.log(`listening on http://localhost:${port}`);
  });

  const shutdown = () => server.close(() => process.exit(0));
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}
