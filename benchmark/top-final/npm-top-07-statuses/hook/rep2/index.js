const http = require('http');
const statuses = require('statuses');

const server = http.createServer((req, res) => {
  const match = req.url.match(/^\/status\/(\d{3})$/);

  if (match) {
    const code = Number(match[1]);
    const reasonPhrase = statuses.message[code];

    if (!reasonPhrase) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: `Unknown status code: ${code}` }));
      return;
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ code, reasonPhrase }));
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found. Try GET /status/:code' }));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
