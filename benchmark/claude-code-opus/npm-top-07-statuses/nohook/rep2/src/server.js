import http from 'node:http';
import { STATUS_CODES, reasonPhrase } from './status-codes.js';

function sendJson(res, statusCode, body) {
  const payload = JSON.stringify(body);
  res.writeHead(statusCode, reasonPhrase(statusCode), {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(payload),
  });
  res.end(payload);
}

function sendError(res, statusCode) {
  sendJson(res, statusCode, { error: reasonPhrase(statusCode), status: statusCode });
}

export function handleRequest(req, res) {
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
    const phrase = reasonPhrase(code);
    return phrase ? sendJson(res, 200, { code, phrase }) : sendError(res, 404);
  }

  return sendError(res, 404);
}

export function createServer() {
  return http.createServer((req, res) => {
    try {
      handleRequest(req, res);
    } catch (err) {
      console.error(err);
      if (!res.headersSent) sendError(res, 500);
      else res.destroy(err);
    }
  });
}

// Start only when run directly (not when imported by tests).
if (import.meta.url === `file://${process.argv[1]}`) {
  const port = Number(process.env.PORT) || 3000;
  const server = createServer();
  server.listen(port, () => console.log(`Listening on http://localhost:${port}`));

  const shutdown = () => server.close(() => process.exit(0));
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}
