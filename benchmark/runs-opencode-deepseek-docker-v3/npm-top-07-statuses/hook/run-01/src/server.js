import { createServer } from "node:http";
import { fileURLToPath } from "node:url";
import { STATUS_CODES, getReasonPhrase, getStatusCodeClass } from "./status-codes.js";

const HOST = process.env.HOST ?? "0.0.0.0";
const PORT = Number(process.env.PORT ?? 3000);

function sendJson(res, status, body) {
  const phrase = getReasonPhrase(status) ?? "Unknown";
  const payload = JSON.stringify(body, null, 2);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(payload),
  });
  res.statusMessage = phrase;
  res.end(payload);
}

export function createApp() {
  return createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);

    if (req.method === "GET" && url.pathname === "/") {
      sendJson(res, 200, {
        name: "http-status-server",
        endpoints: ["/", "/status/:code"],
        codes: Object.keys(STATUS_CODES).length,
      });
      return;
    }

    const match = url.pathname.match(/^\/status\/(\d{3})$/);
    if (req.method === "GET" && match) {
      const code = Number(match[1]);
      const reason = getReasonPhrase(code);
      if (reason === undefined) {
        sendJson(res, 404, {
          code,
          error: "Unknown status code",
          hint: "See /status/:code for a known HTTP status code",
        });
        return;
      }
      sendJson(res, 200, {
        code,
        reason,
        class: getStatusCodeClass(code),
        category: `${getStatusCodeClass(code)}xx`,
      });
      return;
    }

    sendJson(res, 404, { error: "Not Found", path: url.pathname });
  });
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];

if (isMain) {
  const server = createApp();
  server.listen(PORT, HOST, () => {
    console.log(`http-status-server listening on http://${HOST}:${PORT}`);
  });
}

export default createApp;
