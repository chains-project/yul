import http from "node:http";
import { pathToFileURL } from "node:url";
import { STATUS_CODES, getReasonPhrase, isStatusCode } from "./status-codes.js";

const EMPTY_BODY_CODES = new Set([204, 205, 304]);

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
  });
  res.end(body);
}

export function requestHandler(req, res) {
  const { pathname } = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);

  if (req.method === "GET" && pathname === "/health") {
    return sendJson(res, 200, { status: 200, reason: getReasonPhrase(200) });
  }

  if (req.method === "GET" && pathname === "/status") {
    return sendJson(res, 200, STATUS_CODES);
  }

  const match = /^\/status\/(\d{3})$/.exec(pathname);
  if (req.method === "GET" && match) {
    const code = Number(match[1]);

    if (!isStatusCode(code)) {
      return sendJson(res, 404, { error: `Unknown status code: ${match[1]}` });
    }
    if (code < 200 || code > 599) {
      return sendJson(res, 400, { error: `Status code ${code} cannot be sent as a response` });
    }
    if (EMPTY_BODY_CODES.has(code)) {
      res.writeHead(code);
      return res.end();
    }
    return sendJson(res, code, { status: code, reason: getReasonPhrase(code) });
  }

  return sendJson(res, 404, { status: 404, reason: getReasonPhrase(404) });
}

export function createServer() {
  return http.createServer(requestHandler);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT) || 3000;
  const server = createServer();
  server.listen(port, () => {
    console.log(`HTTP server listening on http://localhost:${server.address().port}`);
  });
}
