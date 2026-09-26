'use strict';

const http = require('http');
const { STATUS_CODES, getReasonPhrase } = require('./statusCodes');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  if (req.url === '/statuses' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(STATUS_CODES, null, 2));
    return;
  }

  const match = req.url.match(/^\/statuses\/(\d{3})$/);
  if (match && req.method === 'GET') {
    const code = Number(match[1]);
    const reason = getReasonPhrase(code);
    if (!reason) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: `Unknown status code ${code}` }));
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ code, reason }));
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not Found' }));
});

server.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
