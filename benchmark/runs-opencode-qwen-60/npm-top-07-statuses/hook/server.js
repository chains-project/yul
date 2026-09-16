const http = require("http");
const { statuses, getStatusText } = require("./statuses");

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  if (req.url === "/statuses") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(statuses, null, 2));
    return;
  }

  const match = req.url.match(/^\/(\d+)$/);
  if (match) {
    const code = parseInt(match[1], 10);
    const reason = getStatusText(code);
    res.writeHead(code, { "Content-Type": "text/plain" });
    res.end(`${code} ${reason}`);
    return;
  }

  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("HTTP Status Server\nGET /statuses - all status codes as JSON\nGET /<code> - look up a status code by number\n");
});

server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}/`);
});