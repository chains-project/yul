import { test } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { getReasonPhrase, isStatusCode } from "../src/status-codes.js";
import { createServer } from "../src/server.js";

test("getReasonPhrase returns known phrases", () => {
  assert.equal(getReasonPhrase(200), "OK");
  assert.equal(getReasonPhrase(404), "Not Found");
  assert.equal(getReasonPhrase(500), "Internal Server Error");
});

test("getReasonPhrase returns undefined for unknown codes", () => {
  assert.equal(getReasonPhrase(299), undefined);
});

test("isStatusCode distinguishes known codes", () => {
  assert.equal(isStatusCode(418), true);
  assert.equal(isStatusCode(999), false);
});

test("server responds with the reason phrase for /status/:code", async () => {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();

  const res = await fetch(`http://127.0.0.1:${port}/status/404`);
  assert.equal(res.status, 404);
  assert.equal(await res.text(), "Not Found");

  server.close();
});
