# http-server

A minimal Node.js HTTP server with a lookup table of HTTP status codes and their standard reason phrases. No dependencies.

## Usage

```sh
npm start          # listens on PORT (default 3000)
npm run dev        # restart on file changes
npm test
```

## Endpoints

| Method | Path                  | Response                                  |
| ------ | --------------------- | ----------------------------------------- |
| GET    | `/status-codes`       | Full table: `{ "200": "OK", ... }`        |
| GET    | `/status-codes/:code` | `{ "code": 404, "reason": "Not Found" }`  |

## Lookup table

```js
import { STATUS_CODES, reasonPhrase, isKnownStatus } from './src/status-codes.js';

reasonPhrase(404);   // "Not Found"
isKnownStatus(299);  // false
```

The table comes from Node's built-in `http.STATUS_CODES` (which follows the IANA registry). It's re-exported with numeric keys and frozen.
