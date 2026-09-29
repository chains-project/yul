'use strict';

const http = require('http');
const { Readable } = require('stream');
const { Broadcast } = require('./broadcast');

/**
 * A readable stream that emits Server-Sent Events on a fixed interval. The
 * timer only runs while the stream is flowing and is cleared on destroy.
 */
function createEventSource(intervalMs) {
  const interval = Number.isFinite(intervalMs) ? intervalMs : 1000;
  let timer = null;
  let counter = 0;

  return new Readable({
    read() {
      if (timer) {
        return;
      }

      timer = setInterval(() => {
        counter += 1;
        this.push(`data: tick ${counter}\n\n`);
      }, interval);
    },
    destroy(error, callback) {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
      callback(error);
    },
  });
}

function sendJson(res, statusCode, body) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(body));
}

function createServer(options = {}) {
  const source = options.source || createEventSource(options.interval);
  const broadcast = new Broadcast(source);

  const server = http.createServer((req, res) => {
    if (req.method === 'GET' && req.url === '/stream') {
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      });
      res.write(': connected\n\n');
      broadcast.pipe(res);
      req.on('close', () => broadcast.unpipe(res));
      return;
    }

    if (req.method === 'POST' && req.url === '/unpipe') {
      const removed = broadcast.unpipeAll();
      for (const destination of removed) {
        destination.end();
      }
      sendJson(res, 200, { unpiped: removed.length });
      return;
    }

    if (req.method === 'GET' && req.url === '/health') {
      sendJson(res, 200, { destinations: broadcast.size });
      return;
    }

    sendJson(res, 404, { error: 'not_found' });
  });

  server.on('close', () => {
    broadcast.unpipeAll();
    if (typeof source.destroy === 'function') {
      source.destroy();
    }
  });

  server.broadcast = broadcast;
  server.source = source;
  return server;
}

if (require.main === module) {
  const port = Number(process.env.PORT) || 3000;
  const server = createServer();

  server.listen(port, () => {
    console.log(`stream server listening on http://localhost:${port}`);
  });

  const shutdown = () => {
    server.close(() => process.exit(0));
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

module.exports = { createServer, createEventSource };
