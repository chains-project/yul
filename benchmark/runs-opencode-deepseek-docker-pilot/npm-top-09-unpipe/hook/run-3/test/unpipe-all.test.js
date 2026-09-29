import test from "node:test";
import assert from "node:assert/strict";
import { Readable, Writable } from "node:stream";
import { unpipeAll, isPiped } from "../src/unpipe-all.js";

function collector() {
  const writes = [];
  const stream = new Writable({
    write(chunk, _encoding, callback) {
      writes.push(chunk.toString());
      callback();
    },
  });
  return { stream, writes };
}

test("unpipes a single destination", async () => {
  const source = new Readable({ read() {} });
  const dest = collector();
  source.pipe(dest.stream);

  const unpiped = new Promise((resolve) => dest.stream.once("unpipe", resolve));
  assert.equal(isPiped(source), true);

  const detached = unpipeAll(source);

  assert.deepEqual(detached, [dest.stream]);
  assert.equal(isPiped(source), false);
  await unpiped;
});

test("unpipes every destination", () => {
  const source = new Readable({ read() {} });
  const a = collector();
  const b = collector();
  const c = collector();
  source.pipe(a.stream);
  source.pipe(b.stream);
  source.pipe(c.stream);

  assert.equal(isPiped(source), true);
  const detached = unpipeAll(source);

  assert.equal(detached.length, 3);
  assert.deepEqual(new Set(detached), new Set([a.stream, b.stream, c.stream]));
  assert.equal(isPiped(source), false);
});

test("is idempotent", () => {
  const source = new Readable({ read() {} });
  const dest = collector();
  source.pipe(dest.stream);

  assert.equal(unpipeAll(source).length, 1);
  assert.deepEqual(unpipeAll(source), []);
});

test("stops a flowing stream", () => {
  const source = new Readable({ read() {} });
  const dest = collector();
  source.pipe(dest.stream);
  assert.equal(source.readableFlowing, true);

  unpipeAll(source);

  assert.equal(source.readableFlowing, false);
});

test("writes stop after unpiping", async () => {
  const source = new Readable({ read() {} });
  const dest = collector();
  source.pipe(dest.stream);

  source.push("before");
  await new Promise((resolve) => setImmediate(resolve));
  unpipeAll(source);
  source.push("after");
  await new Promise((resolve) => setImmediate(resolve));

  assert.deepEqual(dest.writes, ["before"]);
});

test("rejects values without an unpipe method", () => {
  assert.throws(() => unpipeAll(null), TypeError);
  assert.throws(() => unpipeAll(undefined), TypeError);
  assert.throws(() => unpipeAll({}), TypeError);
  assert.throws(() => unpipeAll("stream"), TypeError);
});
