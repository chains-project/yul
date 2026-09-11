const http = require('http');
const statuses = require('statuses');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  if (req.url === '/status') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(statuses.codes.reduce((table, code) => {
      table[code] = statuses.message[code];
      return table;
    }, {})));
    return;
  }

  const code = 404;
  res.writeHead(code, statuses.message[code], { 'Content-Type': 'text/plain' });
  res.end(`${code} ${statuses.message[code]}`);
});

server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
