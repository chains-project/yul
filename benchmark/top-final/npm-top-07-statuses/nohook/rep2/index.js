'use strict';

const http = require('http');
const { getReasonPhrase } = require('./statusCodes');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end(`${200} ${getReasonPhrase(200)}\n`);
    return;
  }

  const match = req.url.match(/^\/status\/(\d{3})$/);
  if (match) {
    const code = Number(match[1]);
    const reason = getReasonPhrase(code);
    if (!reason) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Unknown status code\n');
      return;
    }
    res.writeHead(code, { 'Content-Type': 'text/plain' });
    res.end(`${code} ${reason}\n`);
    return;
  }

  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end(`404 ${getReasonPhrase(404)}\n`);
});

server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
