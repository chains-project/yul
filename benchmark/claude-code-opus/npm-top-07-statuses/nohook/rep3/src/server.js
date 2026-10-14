import { createServer } from 'node:http';
import { pathToFileURL } from 'node:url';
import { STATUS_CODES, reasonPhrase, isKnownStatus } from './status-codes.js';

function sendJson(res, status, body) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body));
}

export function handler(req, res) {
  const { pathname } = new URL(req.url, 'http://localhost');

  if (req.method !== 'GET') {
    return sendJson(res, 405, { error: reasonPhrase(405) });
  }

  if (pathname === '/status-codes') {
    return sendJson(res, 200, STATUS_CODES);
  }

  const match = pathname.match(/^\/status-codes\/(\d{3})$/);
  if (match) {
    const code = Number(match[1]);
    if (!isKnownStatus(code)) {
      return sendJson(res, 404, { error: `Unknown status code: ${code}` });
    }
    return sendJson(res, 200, { code, reason: reasonPhrase(code) });
  }

  return sendJson(res, 404, { error: reasonPhrase(404) });
}

export function createApp() {
  return createServer(handler);
}

// Start listening only when run directly (not when imported by tests).
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT) || 3000;
  createApp().listen(port, () => {
    console.log(`Server listening on http://localhost:${port}`);
  });
}
