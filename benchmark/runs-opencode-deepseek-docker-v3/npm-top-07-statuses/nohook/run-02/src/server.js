import { createServer } from 'node:http';
import { fileURLToPath } from 'node:url';
import { STATUS_CODES, statusMessage } from './status-codes.js';

const DEFAULT_PORT = 3000;

function sendJson(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(payload)
  });
  res.end(payload);
}

export function createApp() {
  return createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host ?? 'localhost'}`);

    if (req.method === 'GET' && url.pathname === '/') {
      return sendJson(res, 200, {
        name: 'http-status-server',
        endpoints: ['GET /', 'GET /status/:code', 'GET /status-codes']
      });
    }

    if (req.method === 'GET' && url.pathname === '/status-codes') {
      return sendJson(res, 200, STATUS_CODES);
    }

    const match = url.pathname.match(/^\/status\/(\d{3})$/);
    if (req.method === 'GET' && match) {
      const code = Number(match[1]);
      const known = Object.hasOwn(STATUS_CODES, code);
      return sendJson(res, known ? code : 404, {
        code,
        message: statusMessage(code),
        known
      });
    }

    return sendJson(res, 404, {
      code: 404,
      message: statusMessage(404)
    });
  });
}

export function startServer(port = Number(process.env.PORT) || DEFAULT_PORT) {
  const server = createApp();
  server.listen(port, () => {
    console.log(`HTTP server listening on http://localhost:${port}`);
  });
  return server;
}

const isMain = process.argv[1] === fileURLToPath(import.meta.url);
if (isMain) {
  startServer();
}
