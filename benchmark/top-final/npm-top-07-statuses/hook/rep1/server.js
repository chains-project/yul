const http = require('http');
const statuses = require('statuses');

const server = http.createServer((req, res) => {
  const code = req.url === '/' ? 200 : 404;
  const reasonPhrase = statuses.message[code];

  res.writeHead(code, reasonPhrase, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ code, reasonPhrase }));
});

const port = process.env.PORT || 3000;
server.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
