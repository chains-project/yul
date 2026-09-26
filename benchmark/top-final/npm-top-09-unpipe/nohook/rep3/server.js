const http = require('http');
const fs = require('fs');
const path = require('path');
const { PassThrough } = require('stream');
const unpipe = require('unpipe');

const UPLOAD_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);

const server = http.createServer((req, res) => {
  if (req.method !== 'POST' || req.url !== '/upload') {
    res.writeHead(404);
    res.end('Not found');
    return;
  }

  const filePath = path.join(UPLOAD_DIR, `upload-${Date.now()}.bin`);
  const fileStream = fs.createWriteStream(filePath);
  const echoStream = new PassThrough();

  req.pipe(fileStream);
  req.pipe(echoStream);
  echoStream.pipe(res);

  const detach = () => {
    // req.unpipe() alone can leave listeners/destinations attached
    // inconsistently depending on the stream implementation, so use
    // unpipe() to reliably detach req from every destination it's piped to.
    unpipe(req);
    fileStream.end();
  };

  req.on('aborted', detach);
  req.on('error', detach);
  fileStream.on('error', detach);
  req.on('end', () => fileStream.end());
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});

module.exports = server;
