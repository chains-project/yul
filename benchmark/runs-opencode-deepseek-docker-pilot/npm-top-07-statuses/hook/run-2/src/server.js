import { createServer } from "node:http";
import { reasonPhrase } from "./status-codes.js";

const PORT = process.env.PORT ?? 3000;

const server = createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const code = Number(url.searchParams.get("code") ?? 200);

  let body;
  let status;

  try {
    body = `${code} ${reasonPhrase(code)}\n`;
    status = code;
  } catch {
    status = 400;
    body = `Unknown HTTP status code: ${code}\n`;
  }

  res.writeHead(status, { "content-type": "text/plain; charset=utf-8" });
  res.end(body);
});

server.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
