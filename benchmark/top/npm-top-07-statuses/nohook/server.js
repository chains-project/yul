const http = require('http');
const statuses = require('statuses');

// statuses.message is the code -> reason phrase lookup table (e.g. 404 -> "Not Found")
const server = http.createServer((req, res) => {
  if (req.url === '/') {
    const table = Object.entries(statuses.message).map(
      ([code, phrase]) => ({ code: Number(code), phrase })
    );
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(table));
    return;
  }

  const match = req.url.match(/^\/status\/(\d+)$/);
  if (match) {
    const code = Number(match[1]);
    const phrase = statuses.message[code];
    if (!phrase) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: `Unknown status code: ${code}` }));
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ code, phrase }));
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

const port = process.env.PORT || 3000;
server.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
