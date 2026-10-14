import { test } from 'node:test';
import assert from 'node:assert/strict';
import { PassThrough, Readable } from 'node:stream';
import { unpipeAll } from '../src/unpipe-all.js';

test('detaches all destinations', () => {
  const src = new PassThrough();
  const a = new PassThrough();
  const b = new PassThrough();
  src.pipe(a);
  src.pipe(b);
  assert.equal(src.listenerCount('data'), 2);
  assert.equal(src._readableState.pipes.length, 2);

  unpipeAll(src);

  assert.equal(src._readableState.pipes.length, 0);
  assert.equal(src.listenerCount('data'), 0);
  assert.equal(src.isPaused(), true);
});

test('emits unpipe on every destination', () => {
  const src = new PassThrough();
  const dests = [new PassThrough(), new PassThrough(), new PassThrough()];
  let count = 0;
  for (const d of dests) {
    d.on('unpipe', (s) => { assert.equal(s, src); count++; });
    src.pipe(d);
  }
  unpipeAll(src);
  assert.equal(count, 3);
});

test('no data flows to destinations after unpipe', async () => {
  const src = new PassThrough();
  const dest = new PassThrough();
  const received = [];
  dest.on('data', (c) => received.push(c.toString()));
  src.pipe(dest);
  src.write('before');
  await new Promise((r) => setImmediate(r));
  unpipeAll(src);
  src.write('after');
  await new Promise((r) => setImmediate(r));
  assert.deepEqual(received, ['before']);
  assert.equal(src.read().toString(), 'after'); // data retained, not lost
});

test('is safe on a stream with no destinations', () => {
  const src = Readable.from([]);
  assert.doesNotThrow(() => unpipeAll(src));
});

test('rejects non-streams', () => {
  assert.throws(() => unpipeAll(null), TypeError);
  assert.throws(() => unpipeAll({}), TypeError);
});
