import http from 'node:http';
import { pathToFileURL } from 'node:url';
import { STATUS_CODES, getReasonPhrase, isKnownStatus } from './statusCodes.js';

function sendJson(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(payload),
  });
  res.end(payload);
}

function sendError(res, status) {
  sendJson(res, status, { error: { status, message: getReasonPhrase(status) } });
}

export function createServer() {
  return http.createServer((req, res) => {
    const { pathname } = new URL(req.url, 'http://localhost');

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.setHeader('Allow', 'GET, HEAD');
      return sendError(res, 405);
    }

    if (pathname === '/health') {
      return sendJson(res, 200, { status: 'ok' });
    }

    if (pathname === '/status-codes') {
      return sendJson(res, 200, STATUS_CODES);
    }

    const match = pathname.match(/^\/status-codes\/(\d{3})$/);
    if (match) {
      const code = Number(match[1]);
      if (!isKnownStatus(code)) return sendError(res, 404);
      return sendJson(res, 200, { code, phrase: getReasonPhrase(code) });
    }

    return sendError(res, 404);
  });
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT) || 3000;
  const server = createServer();
  server.listen(port, () => console.log(`Listening on http://localhost:${port}`));

  const shutdown = () => server.close(() => process.exit(0));
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}
