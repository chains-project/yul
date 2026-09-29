import { createServer } from 'node:http';
import { statusCodes, reasonPhrase, hasStatus } from './status.js';

const PORT = process.env.PORT || 3000;

function sendJson(res, status, body) {
  const payload = JSON.stringify(body, null, 2);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(payload),
  });
  res.end(payload);
}

const server = createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (req.method === 'GET' && url.pathname === '/') {
    sendJson(res, 200, statusCodes);
    return;
  }

  const match = url.pathname.match(/^\/status\/(\d{3})$/);
  if (req.method === 'GET' && match) {
    const code = Number(match[1]);
    if (hasStatus(code)) {
      sendJson(res, 200, { code, reason: reasonPhrase(code) });
    } else {
      sendJson(res, 404, { error: `Unknown status code: ${code}` });
    }
    return;
  }

  sendJson(res, 404, { error: 'Not Found' });
});

server.listen(PORT, () => {
  console.log(`HTTP status server listening on http://localhost:${PORT}`);
});
