import http from "node:http";
import { STATUS_CODES, reasonPhrase } from "./statusCodes.js";

export function createServer() {
  return http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);

    if (url.pathname === "/status" || url.pathname === "/status/") {
      const param = url.searchParams.get("code");
      const code = param === null ? Number.NaN : Number(param);
      const status = Number.isInteger(code) && code in STATUS_CODES ? code : 200;
      const body = JSON.stringify({
        code: status,
        reason: reasonPhrase(status),
      });

      res.writeHead(status, {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
      });
      res.end(body);
      return;
    }

    if (url.pathname === "/codes" || url.pathname === "/codes/") {
      const body = JSON.stringify(STATUS_CODES);
      res.writeHead(200, {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
      });
      res.end(body);
      return;
    }

    const body = JSON.stringify({
      error: "Not Found",
      hint: "Try /codes or /status?code=404",
    });
    res.writeHead(404, {
      "Content-Type": "application/json",
      "Content-Length": Buffer.byteLength(body),
    });
    res.end(body);
  });
}

const isMain = process.argv[1] && import.meta.url === `file://${process.argv[1]}`;

if (isMain) {
  const port = Number(process.env.PORT ?? 3000);
  const host = process.env.HOST ?? "0.0.0.0";
  createServer().listen(port, host, () => {
    console.log(`HTTP server listening on http://${host}:${port}`);
  });
}
