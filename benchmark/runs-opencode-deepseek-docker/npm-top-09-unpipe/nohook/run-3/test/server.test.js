'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('http');

const { createServer } = require('../src/server');

function listen(server) {
  return new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
}

function request(server, method, path) {
  const { port } = server.address();

  return new Promise((resolve, reject) => {
    const req = http.request({ host: '127.0.0.1', port, method, path }, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => {
        body += chunk;
      });
      res.on('end', () => resolve({ statusCode: res.statusCode, body }));
    });

    req.on('error', reject);
    req.end();
  });
}

function connectStream(server) {
  const { port } = server.address();

  return new Promise((resolve, reject) => {
    const req = http.get({ host: '127.0.0.1', port, path: '/stream' }, (res) => {
      res.setEncoding('utf8');
      resolve({ req, res });
    });

    req.on('error', reject);
  });
}

test('POST /unpipe detaches every connected client', async (t) => {
  const server = createServer({ interval: 10 });
  await listen(server);
  t.after(() => new Promise((resolve) => server.close(resolve)));

  const clients = await Promise.all([connectStream(server), connectStream(server)]);

  await new Promise((resolve) => setTimeout(resolve, 40));
  assert.equal(server.broadcast.size, 2);

  const response = await request(server, 'POST', '/unpipe');
  assert.equal(response.statusCode, 200);
  assert.equal(JSON.parse(response.body).unpiped, 2);
  assert.equal(server.broadcast.size, 0);

  const health = await request(server, 'GET', '/health');
  assert.deepEqual(JSON.parse(health.body), { destinations: 0 });

  for (const client of clients) {
    client.res.destroy();
    client.req.destroy();
  }
});

test('disconnecting a client removes only that destination', async (t) => {
  const server = createServer({ interval: 10 });
  await listen(server);
  t.after(() => new Promise((resolve) => server.close(resolve)));

  const first = await connectStream(server);
  const second = await connectStream(server);
  await new Promise((resolve) => setTimeout(resolve, 20));
  assert.equal(server.broadcast.size, 2);

  first.res.destroy();
  first.req.destroy();
  await new Promise((resolve) => setTimeout(resolve, 20));
  assert.equal(server.broadcast.size, 1);

  second.res.destroy();
  second.req.destroy();
});
