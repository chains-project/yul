const http = require('http');
const fs = require('fs');
const path = require('path');
const unpipe = require('unpipe');

const FILE_PATH = path.join(__dirname, 'data.txt');

const server = http.createServer((req, res) => {
  const source = fs.createReadStream(FILE_PATH);

  source.on('error', (err) => {
    unpipe(source);
    res.statusCode = 500;
    res.end('Failed to read file');
  });

  req.on('close', () => {
    unpipe(source);
    source.destroy();
  });

  source.pipe(res);
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
