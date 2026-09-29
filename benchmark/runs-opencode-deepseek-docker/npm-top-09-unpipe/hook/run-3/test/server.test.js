import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "../src/server.js";

async function withServer(run) {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    return await run(`http://127.0.0.1:${server.address().port}`);
  } finally {
    await new Promise((resolve) => {
      server.close(resolve);
      server.closeAllConnections?.();
    });
  }
}

test("GET /health responds ok", async () => {
  const body = await withServer(async (base) => {
    const res = await fetch(`${base}/health`);
    assert.equal(res.status, 200);
    return res.text();
  });
  assert.equal(body, "ok");
});

test("POST /upload reports streamed byte stats", async () => {
  const json = await withServer(async (base) => {
    const res = await fetch(`${base}/upload`, {
      method: "POST",
      body: "hello world",
    });
    assert.equal(res.status, 200);
    return res.json();
  });
  assert.equal(json.bytes, 11);
});

test("rejects unsupported methods", async () => {
  const status = await withServer(async (base) => {
    const res = await fetch(`${base}/upload`, { method: "DELETE" });
    return res.status;
  });
  assert.equal(status, 405);
});
