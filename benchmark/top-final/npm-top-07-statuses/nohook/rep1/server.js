const http = require('http');
const { getReasonPhrase, getStatusCode } = require('http-status-codes');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  if (req.url === '/') {
    const status = getStatusCode('OK');
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status, reason: getReasonPhrase(status) }));
    return;
  }

  const status = getStatusCode('Not Found');
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ status, reason: getReasonPhrase(status) }));
});

server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
