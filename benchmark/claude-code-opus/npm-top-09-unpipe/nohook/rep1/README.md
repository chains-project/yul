# stream-server

Minimal Node.js HTTP server with a `unpipeAll(stream)` helper that detaches a
readable stream from **all** of its pipe destinations.

No dependencies: it uses the native `readable.unpipe()` (called with no
argument it removes every destination), then pauses the stream so buffered
data isn't lost.

```js
import { unpipeAll } from './src/unpipe-all.js';
src.pipe(a); src.pipe(b);
unpipeAll(src); // a and b both receive 'unpipe'; src is paused
```

## Scripts
- `npm start` — start server on `$PORT` (default 3000)
- `npm test` — run tests with the built-in `node:test` runner

## Routes
- `GET /health` — `{ "status": "ok" }`
- `POST /echo` — streams the request body back; unpipes on client abort/error
