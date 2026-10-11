import http from "node:http";
import { getReasonPhrase, sendStatus, isStatusCode } from "./status-codes.js";

const PORT = process.env.PORT ?? 3000;
const HOST = process.env.HOST ?? "127.0.0.1";

function handleRequest(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (url.pathname === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: getReasonPhrase(200) }));
    return;
  }

  const match = url.pathname.match(/^\/status\/(\d{3})$/);
  if (match) {
    const code = Number(match[1]);
    if (!isStatusCode(code)) {
      sendStatus(res, 400, `Unknown status code: ${code}`);
      return;
    }
    sendStatus(res, code);
    return;
  }

  if (url.pathname === "/") {
    res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("HTTP status server. Try GET /status/404 or /health\n");
    return;
  }

  sendStatus(res, 404);
}

export function createServer() {
  return http.createServer(handleRequest);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  createServer().listen(PORT, HOST, () => {
    console.log(`Server listening on http://${HOST}:${PORT}`);
  });
}
