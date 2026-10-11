import { test } from "node:test";
import assert from "node:assert/strict";
import { STATUS_CODES, getReasonPhrase, getStatusCodeClass } from "../src/status-codes.js";
import { createApp } from "../src/server.js";

test("getReasonPhrase returns standard phrases", () => {
  assert.equal(getReasonPhrase(200), "OK");
  assert.equal(getReasonPhrase(404), "Not Found");
  assert.equal(getReasonPhrase(500), "Internal Server Error");
  assert.equal(getReasonPhrase("418"), "I'm a teapot");
});

test("getReasonPhrase returns undefined for unknown codes", () => {
  assert.equal(getReasonPhrase(999), undefined);
  assert.equal(getReasonPhrase("nope"), undefined);
});

test("getStatusCodeClass maps codes to their class", () => {
  assert.equal(getStatusCodeClass(204), 2);
  assert.equal(getStatusCodeClass(301), 3);
  assert.equal(getStatusCodeClass(503), 5);
  assert.equal(getStatusCodeClass(42), undefined);
  assert.equal(getStatusCodeClass(600), undefined);
});

test("all codes are valid 3-digit HTTP status codes", () => {
  for (const key of Object.keys(STATUS_CODES)) {
    const code = Number(key);
    assert.ok(Number.isInteger(code) && code >= 100 && code <= 599, `invalid code ${key}`);
  }
});

test("GET /status/:code returns reason phrase", async () => {
  const server = createApp();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  try {
    const res = await fetch(`http://127.0.0.1:${port}/status/404`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.deepEqual(body, { code: 404, reason: "Not Found", class: 4, category: "4xx" });
  } finally {
    server.close();
  }
});

test("GET /status/:code returns 404 for unknown codes", async () => {
  const server = createApp();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  try {
    const res = await fetch(`http://127.0.0.1:${port}/status/999`);
    assert.equal(res.status, 404);
    const body = await res.json();
    assert.equal(body.code, 999);
  } finally {
    server.close();
  }
});
