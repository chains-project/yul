const http = require('http');
const fs = require('fs');
const path = require('path');
const { unpipe } = require('unpipe');

const PORT = process.env.PORT || 3000;

function unpipeAllDestinations(stream) {
  unpipe(stream);
}

function setupStreamCleanup(readStream, res, req) {
  req.on('close', () => {
    if (readStream.destroyed) return;
    unpipeAllDestinations(readStream);
    readStream.destroy();
  });

  res.on('close', () => {
    if (readStream.destroyed) return;
    unpipeAllDestinations(readStream);
    readStream.destroy();
  });
}

function createFileStreamHandler(filePath) {
  return (req, res) => {
    if (req.method !== 'GET') {
      res.writeHead(405);
      res.end('Method Not Allowed');
      return;
    }

    const readStream = fs.createReadStream(filePath);

    readStream.on('error', (err) => {
      if (res.headersSent) return;
      if (err.code === 'ENOENT') {
        res.writeHead(404);
        res.end('File not found');
      } else {
        res.writeHead(500);
        res.end('Server error');
      }
    });

    setupStreamCleanup(readStream, res, req);

    unpipeAllDestinations(readStream);

    readStream.pipe(res);
  };
}

function createRequestBodyHandler(handler) {
  return (req, res) => {
    if (req.method !== 'POST') {
      res.writeHead(405);
      res.end('Method Not Allowed');
      return;
    }

    unpipe(req);

    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
      if (body.length > 1e6) {
        unpipe(req);
        req.destroy();
        res.writeHead(413);
        res.end('Payload too large');
      }
    });

    req.on('end', () => {
      try {
        handler(body, req, res);
      } catch (err) {
        if (!res.headersSent) {
          res.writeHead(500);
          res.end('Internal server error');
        }
      }
    });

    req.on('error', (err) => {
      unpipe(req);
      if (!res.headersSent) {
        res.writeHead(500);
        res.end('Request error');
      }
    });
  };
}

function createMultiStreamHandler() {
  return (req, res) => {
    if (req.method !== 'GET') {
      res.writeHead(405);
      res.end('Method Not Allowed');
      return;
    }

    const readStreams = [
      fs.createReadStream(path.join(__dirname, '..', 'sample.txt')),
      fs.createReadStream(path.join(__dirname, '..', 'config.txt'))
    ];

    readStreams.forEach((stream) => {
      unpipeAllDestinations(stream);
      setupStreamCleanup(stream, res, req);
      stream.pipe(res);
    });
  };
}

const server = http.createServer((req, res) => {
  const routes = [
    { path: '/stream', method: 'GET', handler: createFileStreamHandler(path.join(__dirname, '..', 'sample.txt')) },
    { path: '/echo', method: 'POST', handler: createRequestBodyHandler((body) => {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end(`Received: ${body}`);
    })},
    { path: '/multi', method: 'GET', handler: createMultiStreamHandler() }
  ];

  const route = routes.find(r => r.path === req.url && r.method === req.method);
  if (route) {
    route.handler(req, res);
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

module.exports = { server };