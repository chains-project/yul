import http from 'node:http';
import { PassThrough } from 'node:stream';
import { fileURLToPath } from 'node:url';
import { unpipe } from './unpipe.js';

export function createServer() {
  return http.createServer((req, res) => {
    // Example: tee the request body to a side-channel while echoing it back.
    const audit = new PassThrough();
    audit.resume();

    req.pipe(res);
    req.pipe(audit);

    // If the client goes away, detach the request from all destinations
    // so nothing keeps writing to a dead response.
    res.on('close', () => {
      if (!res.writableFinished) unpipe(req);
    });
  });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT) || 3000;
  createServer().listen(port, () => {
    console.log(`listening on http://localhost:${port}`);
  });
}
