import http from 'node:http';
import { STATUS_CODES, getReasonPhrase, getStatusClass } from './statusCodes.js';

function sendJson(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, getReasonPhrase(status), {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(payload),
  });
  res.end(payload);
}

function sendError(res, status, message) {
  sendJson(res, status, {
    error: { status, reason: getReasonPhrase(status), message },
  });
}

export function createServer() {
  return http.createServer((req, res) => {
    const { pathname } = new URL(req.url, 'http://localhost');

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.setHeader('Allow', 'GET, HEAD');
      return sendError(res, 405, `Method ${req.method} not allowed`);
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
      const reason = getReasonPhrase(code);
      if (!reason) return sendError(res, 404, `Unknown status code ${code}`);
      return sendJson(res, 200, { code, reason, class: getStatusClass(code) });
    }

    sendError(res, 404, `No route for ${pathname}`);
  });
}
