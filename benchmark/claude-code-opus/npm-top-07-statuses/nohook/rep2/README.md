# http-server

Minimal Node.js HTTP server (no dependencies) with a lookup table of HTTP status codes and reason phrases.

## Usage

```sh
npm start          # listens on PORT (default 3000)
npm run dev        # restarts on file changes
npm test
```

## Endpoints

| Method | Path                  | Description                         |
| ------ | --------------------- | ----------------------------------- |
| GET    | `/health`             | Health check                        |
| GET    | `/status-codes`       | Full status-code → phrase table     |
| GET    | `/status-codes/:code` | Phrase for one code (404 if unknown) |

## Status codes module

```js
import { STATUS_CODES, reasonPhrase, statusClass } from './src/status-codes.js';

reasonPhrase(404); // 'Not Found'
statusClass(503);  // 'server-error'
```

Phrases follow the IANA registry / RFC 9110 (e.g. 413 is "Content Too Large", 422 is "Unprocessable Content").
