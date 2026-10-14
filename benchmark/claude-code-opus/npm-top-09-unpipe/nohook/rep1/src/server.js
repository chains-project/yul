import http from 'node:http';
import { pathToFileURL } from 'node:url';
import { unpipeAll } from './unpipe-all.js';

export function createServer() {
  return http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/echo') {
      // Stream the request body back to the client.
      req.pipe(res);

      // If either side goes away early, detach the request from all destinations.
      const cleanup = () => {
        unpipeAll(req);
        req.resume(); // drain remaining input so the socket can be reused/closed
      };
      req.on('error', cleanup);
      res.on('close', () => {
        if (!res.writableFinished) cleanup();
      });
      return;
    }

    if (req.method === 'GET' && req.url === '/health') {
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ status: 'ok' }));
      return;
    }

    res.writeHead(404, { 'content-type': 'text/plain' });
    res.end('Not Found');
  });
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT) || 3000;
  createServer().listen(port, () => {
    console.log(`Server listening on http://localhost:${port}`);
  });
}
