import { createServer } from "node:http";
import { STATUS_CODES, getReasonPhrase } from "./status-codes.js";

const PORT = Number(process.env.PORT) || 3000;

const server = createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);

  if (url.pathname === "/status-codes") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify(STATUS_CODES, null, 2));
    return;
  }

  const match = url.pathname.match(/^\/status\/(\d{3})$/);
  if (match) {
    const code = Number(match[1]);
    res.writeHead(200, { "content-type": "application/json" });
    res.end(
      JSON.stringify({
        code,
        reason: getReasonPhrase(code),
      }),
    );
    return;
  }

  res.writeHead(404, { "content-type": "application/json" });
  res.end(JSON.stringify({ error: getReasonPhrase(404) }));
});

server.listen(PORT, () => {
  console.log(`HTTP server listening on http://localhost:${PORT}`);
});
