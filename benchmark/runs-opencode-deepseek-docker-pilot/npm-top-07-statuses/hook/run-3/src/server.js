import http from "node:http";
import { getReasonPhrase } from "./status-codes.js";

const PORT = Number(process.env.PORT) || 3000;

function sendJson(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(payload),
  });
  res.end(payload);
}

export function createServer() {
  return http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);

    if (req.method === "GET" && url.pathname === "/") {
      return sendJson(res, 200, {
        name: "http-status-server",
        endpoints: ["/", "/status/:code"],
      });
    }

    const match = url.pathname.match(/^\/status\/(\d{3})$/);
    if (req.method === "GET" && match) {
      const code = Number(match[1]);
      return sendJson(res, code, {
        code,
        reason: getReasonPhrase(code),
      });
    }

    return sendJson(res, 404, {
      code: 404,
      reason: getReasonPhrase(404),
    });
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  createServer().listen(PORT, () => {
    console.log(`Server listening on http://localhost:${PORT}`);
  });
}
