import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "../src/server.js";

let server;
let baseUrl;

before(async () => {
  server = createServer();
  await new Promise((resolve) => server.listen(0, resolve));
  baseUrl = `http://localhost:${server.address().port}`;
});

after(() => new Promise((resolve) => server.close(resolve)));

test("GET /health returns 200 OK", async () => {
  const res = await fetch(`${baseUrl}/health`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { status: 200, reason: "OK" });
});

test("GET /status returns the full lookup table", async () => {
  const res = await fetch(`${baseUrl}/status`);
  assert.equal(res.status, 200);
  const body = await res.json();
  assert.equal(body["200"], "OK");
  assert.equal(body["404"], "Not Found");
  assert.equal(body["503"], "Service Unavailable");
});

test("GET /status/:code mirrors the code and reason phrase", async () => {
  const res = await fetch(`${baseUrl}/status/404`);
  assert.equal(res.status, 404);
  assert.deepEqual(await res.json(), { status: 404, reason: "Not Found" });
});

test("GET /status/:code with an unknown code returns 404", async () => {
  const res = await fetch(`${baseUrl}/status/999`);
  assert.equal(res.status, 404);
});

test("bodyless status codes return an empty body", async () => {
  const res = await fetch(`${baseUrl}/status/204`);
  assert.equal(res.status, 204);
  assert.equal(await res.text(), "");
});

test("unknown routes return 404", async () => {
  const res = await fetch(`${baseUrl}/does-not-exist`);
  assert.equal(res.status, 404);
});
