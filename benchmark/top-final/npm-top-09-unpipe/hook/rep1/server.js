'use strict';

const http = require('http');
const crypto = require('crypto');
const { PassThrough } = require('stream');
const unpipe = require('unpipe');

// Streams data to the client while also hashing it on the side.
// If the client disconnects mid-stream, `unpipe(source)` detaches
// the source from *all* of its destinations (response + hasher) in
// one call, so neither pipe keeps writing to a socket/stream that's
// no longer being consumed.
function streamWithHash(source, res) {
  const hasher = crypto.createHash('sha256');
  const hashSink = new PassThrough();
  hashSink.on('data', (chunk) => hasher.update(chunk));
  hashSink.on('end', () => {
    console.log('sha256:', hasher.digest('hex'));
  });

  source.pipe(res);
  source.pipe(hashSink);

  res.on('close', () => {
    if (!res.writableEnded) {
      unpipe(source);
      source.destroy();
    }
  });
}

const server = http.createServer((req, res) => {
  if (req.method !== 'GET' || req.url !== '/') {
    res.writeHead(404);
    res.end('Not found');
    return;
  }

  res.writeHead(200, { 'Content-Type': 'text/plain' });

  const source = new PassThrough();
  streamWithHash(source, res);

  let i = 0;
  const interval = setInterval(() => {
    if (i++ >= 20 || source.destroyed) {
      clearInterval(interval);
      source.end();
      return;
    }
    source.write(`chunk ${i}\n`);
  }, 100);

  source.on('close', () => clearInterval(interval));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
