import test from "node:test";
import assert from "node:assert/strict";
import { Readable, Writable } from "node:stream";
import { destinations, pipeTo, unpipeAll } from "../src/unpipe-all.js";

class Collector extends Writable {
  constructor() {
    super();
    this.chunks = [];
  }

  _write(chunk, _encoding, callback) {
    this.chunks.push(chunk.toString());
    callback();
  }
}

test("unpipeAll detaches every tracked destination", () => {
  const source = Readable.from(["a", "b", "c"]);
  const first = new Collector();
  const second = new Collector();

  pipeTo(source, first);
  pipeTo(source, second);

  assert.equal(destinations(source).length, 2);

  unpipeAll(source);

  assert.equal(destinations(source).length, 0);
  assert.equal(source._readableState.pipes.length, 0);
});

test("unpipeAll handles a destination piped more than once", () => {
  const source = Readable.from(["a"]);
  const collector = new Collector();

  source.pipe(collector);
  source.pipe(collector);
  assert.equal(source._readableState.pipes.length, 2);

  unpipeAll(source);

  assert.equal(source._readableState.pipes.length, 0);
});

test("detached destinations stop receiving data", async () => {
  const source = new Readable({ read() {} });
  const attached = new Collector();
  const detached = new Collector();

  pipeTo(source, attached);
  pipeTo(source, detached);
  unpipeAll(source);

  pipeTo(source, attached);
  source.push("only-attached");
  source.push(null);

  await new Promise((resolve) => attached.on("finish", resolve));

  assert.deepEqual(detached.chunks, []);
  assert.deepEqual(attached.chunks, ["only-attached"]);
});
