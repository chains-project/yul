const http = require('http');
const { PassThrough } = require('stream');
const unpipe = require('unpipe');

const server = http.createServer((req, res) => {
  const logger = new PassThrough();
  const mirror = new PassThrough();

  req.pipe(logger);
  req.pipe(mirror);

  req.on('aborted', () => {
    unpipe(req);
    res.destroy();
  });

  mirror.on('data', (chunk) => {
    res.write(chunk);
  });

  req.on('end', () => {
    unpipe(req);
    res.end();
  });
});

server.listen(3000, () => {
  console.log('Server listening on port 3000');
});
