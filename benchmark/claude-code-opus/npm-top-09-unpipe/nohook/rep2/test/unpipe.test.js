import { test } from 'node:test';
import assert from 'node:assert/strict';
import { PassThrough, Writable } from 'node:stream';
import { unpipeAll } from '../src/unpipe.js';

test('removes every pipe destination', () => {
  const source = new PassThrough();
  const a = new PassThrough();
  const b = new PassThrough();
  const c = new PassThrough();

  source.pipe(a);
  source.pipe(b);
  source.pipe(c);
  assert.equal(source.listenerCount('data'), 3);

  unpipeAll(source);

  assert.equal(source.listenerCount('data'), 0);
  assert.equal(source.readableFlowing, false);
});

test('emits unpipe on each destination', () => {
  const source = new PassThrough();
  const dests = [new PassThrough(), new PassThrough()];
  const seen = [];

  for (const d of dests) {
    d.on('unpipe', (src) => seen.push(src));
    source.pipe(d);
  }

  unpipeAll(source);

  assert.deepEqual(seen, [source, source]);
});

test('destinations receive no data after unpipe', async () => {
  const source = new PassThrough();
  const chunks = [];
  const sink = new Writable({
    write(chunk, _enc, cb) {
      chunks.push(chunk.toString());
      cb();
    },
  });

  source.pipe(sink);
  source.write('before');
  await new Promise((r) => setImmediate(r));

  unpipeAll(source);
  source.write('after');
  await new Promise((r) => setImmediate(r));

  assert.deepEqual(chunks, ['before']);
});

test('is safe on a stream with no destinations', () => {
  const source = new PassThrough();
  assert.equal(unpipeAll(source), source);
  assert.equal(unpipeAll(source), source);
});

test('throws on non-streams', () => {
  assert.throws(() => unpipeAll(), TypeError);
  assert.throws(() => unpipeAll({}), TypeError);
});
