# http-server

Minimal Node.js HTTP server with no dependencies (Node >= 20).

```sh
npm start        # listen on $PORT (default 3000)
npm run dev      # restart on file changes
npm test         # run tests with node:test
```

## Status code lookup

`src/statusCodes.js` exports:

- `STATUS_CODES`: a frozen `{ [code: number]: reasonPhrase }` table, taken from Node's built-in `http.STATUS_CODES` (which follows the IANA registry)
- `getReasonPhrase(code)`: returns the phrase, or `undefined` if the code isn't registered
- `isKnownStatus(code)`: returns a boolean

## Endpoints

| Method | Path                  | Description                        |
| ------ | --------------------- | ---------------------------------- |
| GET    | `/health`             | Health check                       |
| GET    | `/status-codes`       | Full status code table             |
| GET    | `/status-codes/:code` | Phrase for one code (404 if unknown) |
