import http from "node:http";
import { reasonPhrase, statusCodes } from "./status-codes.js";

const port = Number(process.env.PORT ?? 3000);

const server = http.createServer((req, res) => {
  if (req.url === "/status-codes") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify(statusCodes));
    return;
  }

  const code = 200;
  res.writeHead(code, { "content-type": "text/plain" });
  res.end(`${code} ${reasonPhrase(code)}\n`);
});

server.listen(port, () => {
  console.log(`Listening on http://localhost:${port}`);
});
