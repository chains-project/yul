# http-server

Minimal Node.js HTTP server (no dependencies) with a lookup table of HTTP status codes and reason phrases.

## Usage

```sh
npm start          # listens on $PORT (default 3000)
npm run dev        # restart on file changes
npm test
```

## Endpoints

| Method | Path                  | Description                     |
| ------ | --------------------- | ------------------------------- |
| GET    | `/health`             | Liveness check                  |
| GET    | `/status-codes`       | Full code → reason phrase table |
| GET    | `/status-codes/:code` | `{ code, phrase }` or 404       |

## Status code table

`src/status-codes.js` exports:

- `STATUS_CODES` — frozen object mapping code → phrase (IANA registry / RFC 9110 names)
- `reasonPhrase(code)` — phrase or `undefined`
- `statusClass(code)` — `'informational' | 'success' | 'redirection' | 'client_error' | 'server_error'`
