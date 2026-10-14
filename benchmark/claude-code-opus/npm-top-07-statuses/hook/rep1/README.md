# http-server

Minimal Node.js HTTP server (no dependencies) with a lookup table of HTTP
status codes and their standard reason phrases.

## Usage

```sh
npm start          # PORT=3000 by default
npm run dev        # restart on file changes
npm test
```

## Status code table

```js
import { STATUS_CODES, getReasonPhrase, getStatusClass } from './src/statusCodes.js';

getReasonPhrase(404); // 'Not Found'
getStatusClass(404);  // 'client_error'
```

Phrases follow the IANA registry / RFC 9110.

## Endpoints

| Method | Path                   | Description                         |
| ------ | ---------------------- | ----------------------------------- |
| GET    | `/health`              | Liveness check                      |
| GET    | `/status-codes`        | Full code → reason phrase table     |
| GET    | `/status-codes/:code`  | Reason phrase and class for a code  |
