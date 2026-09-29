"use strict";

const test = require("node:test");
const assert = require("node:assert");
const { PassThrough } = require("stream");
const unpipe = require("unpipe");
const { createSource } = require("../index");

test("unpipes a stream from all destinations", async () => {
  const source = createSource();
  const a = new PassThrough();
  const b = new PassThrough();

  let aChunks = 0;
  let bChunks = 0;
  a.on("data", () => aChunks++);
  b.on("data", () => bChunks++);

  source.pipe(a);
  source.pipe(b);

  await new Promise((resolve) => setImmediate(resolve));
  const seenBefore = aChunks;
  assert.ok(seenBefore > 0, "destination received data before unpipe");

  unpipe(source);

  const after = { a: aChunks, b: bChunks };
  await new Promise((resolve) => setTimeout(resolve, 20));

  assert.strictEqual(aChunks, after.a);
  assert.strictEqual(bChunks, after.b);
});
