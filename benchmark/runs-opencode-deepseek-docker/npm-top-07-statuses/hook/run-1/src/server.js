import http from 'node:http';
import { STATUS_CODES, reasonPhrase } from './status-codes.js';

const PORT = process.env.PORT ?? 3000;

function sendJson(res, status, body) {
  const payload = JSON.stringify(body, null, 2);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(payload)
  });
  res.end(payload);
}

export function createServer() {
  return http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host ?? 'localhost'}`);

    if (url.pathname === '/status' || url.pathname === '/status/') {
      sendJson(res, 200, STATUS_CODES);
      return;
    }

    const match = url.pathname.match(/^\/status\/(\d{3})$/);
    if (match) {
      const code = Number(match[1]);
      const phrase = reasonPhrase(code);
      if (!phrase) {
        sendJson(res, 404, { error: 'Unknown status code', code });
        return;
      }
      sendJson(res, 200, { code, phrase });
      return;
    }

    sendJson(res, 404, { error: 'Not Found', path: url.pathname });
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  createServer().listen(PORT, () => {
    console.log(`Server listening on http://localhost:${PORT}`);
  });
}
