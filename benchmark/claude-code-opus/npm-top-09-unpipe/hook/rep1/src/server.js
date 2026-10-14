'use strict';

const http = require('node:http');
const { Readable } = require('node:stream');
const { unpipeAll } = require('./unpipe');

/**
 * A slow, finite source so that clients can disconnect mid-stream.
 */
function createTickSource({ count = 50, intervalMs = 100 } = {}) {
  let i = 0;
  let timer = null;
  return new Readable({
    read() {
      if (timer) return;
      timer = setTimeout(() => {
        timer = null;
        i += 1;
        this.push(i > count ? null : `tick ${i}\n`);
      }, intervalMs);
    },
    destroy(err, cb) {
      clearTimeout(timer);
      cb(err);
    },
  });
}

function createServer(options = {}) {
  return http.createServer((req, res) => {
    if (req.method === 'GET' && req.url === '/health') {
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    if (req.method === 'GET' && req.url === '/stream') {
      const source = createTickSource(options.source);
      res.writeHead(200, { 'content-type': 'text/plain; charset=utf-8' });
      source.pipe(res);

      // If the client goes away before we finish, detach the source from all
      // destinations and release it so it stops producing data.
      res.on('close', () => {
        if (!res.writableFinished) {
          unpipeAll(source);
          source.destroy();
        }
      });
      if (options.onSource) options.onSource(source);
      return;
    }

    res.writeHead(404, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ error: 'not found' }));
  });
}

if (require.main === module) {
  const port = Number(process.env.PORT) || 3000;
  createServer().listen(port, () => {
    console.log(`listening on http://localhost:${port}`);
  });
}

module.exports = { createServer, createTickSource };
