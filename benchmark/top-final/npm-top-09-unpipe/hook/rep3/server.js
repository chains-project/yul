const http = require('http');
const unpipe = require('unpipe');

const server = http.createServer((req, res) => {
  const passthrough = new (require('stream').PassThrough)();
  req.pipe(passthrough);
  passthrough.pipe(res);

  req.on('aborted', () => {
    unpipe(passthrough);
    res.end();
  });
});

server.listen(3000, () => {
  console.log('Server listening on port 3000');
});
