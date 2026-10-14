import { test } from 'node:test';
import assert from 'node:assert/strict';
import { PassThrough, Readable } from 'node:stream';
import { unpipe } from '../src/unpipe.js';

test('unpipes from all destinations', () => {
  const src = new PassThrough();
  const dests = [new PassThrough(), new PassThrough(), new PassThrough()];
  dests.forEach((d) => src.pipe(d));
  assert.equal(src.listenerCount('data'), dests.length);

  let unpiped = 0;
  dests.forEach((d) => d.on('unpipe', () => unpiped++));

  assert.equal(unpipe(src), src);
  assert.equal(unpiped, 3);
  assert.equal(src.listenerCount('data'), 0);
});

test('data written after unpipe does not reach former destinations', async () => {
  const src = new PassThrough();
  const dest = new PassThrough();
  src.pipe(dest);
  unpipe(src);

  let got = false;
  dest.on('data', () => { got = true; });
  src.write('hello');
  await new Promise((r) => setImmediate(r));
  assert.equal(got, false);
});

test('is a no-op with no destinations, and is idempotent', () => {
  const src = Readable.from([]);
  unpipe(src);
  unpipe(src);
});

test('throws without a stream', () => {
  assert.throws(() => unpipe(), TypeError);
});
