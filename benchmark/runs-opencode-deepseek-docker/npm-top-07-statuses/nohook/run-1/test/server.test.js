'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { createServer } = require('../src/server');

function withServer(run) {
  return async () => {
    const server = createServer();
    await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
    const { port } = server.address();
    try {
      await run(`http://127.0.0.1:${port}`);
    } finally {
      await new Promise((resolve) => {
        server.close(resolve);
        server.closeAllConnections();
      });
    }
  };
}

test('GET /status returns the full lookup table', withServer(async (base) => {
  const res = await fetch(`${base}/status`);
  assert.equal(res.status, 200);
  const body = await res.json();
  assert.equal(body.statusCodes[404], 'Not Found');
}));

test('GET /status/:code responds with that status and phrase', withServer(async (base) => {
  const res = await fetch(`${base}/status/418`);
  assert.equal(res.status, 418);
  assert.equal(res.statusText, "I'm a Teapot");
  assert.deepEqual(await res.json(), { code: 418, reason: "I'm a Teapot" });
}));

test('unknown code returns 400', withServer(async (base) => {
  const res = await fetch(`${base}/status/999`);
  assert.equal(res.status, 400);
}));

test('unknown path returns 404', withServer(async (base) => {
  const res = await fetch(`${base}/nope`);
  assert.equal(res.status, 404);
}));
