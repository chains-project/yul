'use strict';

const { createServer } = require('./server');

const port = Number(process.env.PORT) || 3000;
const host = process.env.HOST || '127.0.0.1';
const server = createServer();

server.listen(port, host, () => {
  const address = server.address();
  console.log(`http-status-server listening on http://${address.address}:${address.port}`);
});

module.exports = server;
