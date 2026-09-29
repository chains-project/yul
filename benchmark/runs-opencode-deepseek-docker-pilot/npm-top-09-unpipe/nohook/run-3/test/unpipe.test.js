'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { Readable, Writable } = require('stream');

const { unpipeAll } = require('../src/unpipe');

function collector() {
  const chunks = [];
  const writable = new Writable({
    write(chunk, encoding, callback) {
      chunks.push(chunk.toString());
      callback();
    },
  });
  writable.chunks = chunks;
  return writable;
}

test('unpipeAll detaches every destination', async () => {
  const source = new Readable({ read() {} });
  const a = collector();
  const b = collector();

  source.pipe(a);
  source.pipe(b);

  source.push('first');
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(a.chunks, ['first']);
  assert.deepEqual(b.chunks, ['first']);

  const removed = unpipeAll(source, [a, b]);
  assert.deepEqual(removed, [a, b]);
  assert.equal(source._readableState.pipes.length, 0);

  source.push('second');
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(a.chunks, ['first']);
  assert.deepEqual(b.chunks, ['first']);
});

test('unpipeAll detaches destinations even without an explicit list', () => {
  const source = new Readable({ read() {} });
  const destination = collector();

  source.pipe(destination);
  unpipeAll(source);

  source.push('data');
  assert.deepEqual(destination.chunks, []);
  assert.equal(source._readableState.pipes.length, 0);
});

test('unpipeAll falls back to emitting unpipe for custom streams', () => {
  const source = { pipe() {} };
  const destination = new Writable({ write(chunk, encoding, callback) { callback(); } });
  let seen = null;

  destination.on('unpipe', (from) => {
    seen = from;
  });

  unpipeAll(source, [destination]);
  assert.equal(seen, source);
});

test('unpipeAll rejects non-readable sources', () => {
  assert.throws(() => unpipeAll(null), TypeError);
});
