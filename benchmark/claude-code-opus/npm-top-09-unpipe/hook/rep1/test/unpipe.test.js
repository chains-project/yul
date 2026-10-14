'use strict';

const test = require('node:test');
const assert = require('node:assert');
const { PassThrough, Stream, Writable } = require('node:stream');
const http = require('node:http');
const { unpipeAll } = require('../src/unpipe');
const { createServer } = require('../src/server');

function sink() {
  const chunks = [];
  const w = new Writable({
    write(chunk, _enc, cb) {
      chunks.push(chunk.toString());
      cb();
    },
  });
  w.chunks = chunks;
  return w;
}

test('throws without a stream', () => {
  assert.throws(() => unpipeAll(), TypeError);
});

test('unpipes a modern Readable from every destination', async () => {
  const src = new PassThrough();
  const a = sink();
  const b = sink();
  src.pipe(a);
  src.pipe(b);

  src.write('before');
  await new Promise((r) => setImmediate(r));

  assert.strictEqual(unpipeAll(src), src);
  src.write('after');
  await new Promise((r) => setImmediate(r));

  assert.deepStrictEqual(a.chunks, ['before']);
  assert.deepStrictEqual(b.chunks, ['before']);
  assert.strictEqual(src.listenerCount('data'), 0);
});

test('unpipes a legacy Stream from every destination', () => {
  const src = new Stream();
  const a = sink();
  const b = sink();
  src.pipe(a);
  src.pipe(b);

  src.emit('data', 'before');
  unpipeAll(src);
  src.emit('data', 'after');

  assert.deepStrictEqual(a.chunks, ['before']);
  assert.deepStrictEqual(b.chunks, ['before']);
  assert.strictEqual(src.listenerCount('data'), 0);
  assert.strictEqual(src.listenerCount('close'), 0);
});

test('is a no-op for a legacy Stream that is not piped', () => {
  const src = new Stream();
  const onClose = function cleanup() {
    throw new Error('should not be called');
  };
  src.on('close', onClose);
  unpipeAll(src);
  assert.strictEqual(src.listenerCount('close'), 1);
});

test('server unpipes and destroys the source when the client aborts', async () => {
  let source;
  const server = createServer({
    source: { count: 1000, intervalMs: 5 },
    onSource: (s) => (source = s),
  });
  await new Promise((r) => server.listen(0, r));
  const { port } = server.address();

  await new Promise((resolve, reject) => {
    const req = http.get({ port, path: '/stream' }, (res) => {
      res.once('data', () => req.destroy());
    });
    req.on('error', () => {});
    req.on('close', resolve);
    setTimeout(() => reject(new Error('timeout')), 2000);
  });

  // Wait for the server side to observe the disconnect.
  while (!source || !source.destroyed) {
    await new Promise((r) => setTimeout(r, 10));
  }
  assert.strictEqual(source.listenerCount('data'), 0);

  await new Promise((r) => server.close(r));
});
