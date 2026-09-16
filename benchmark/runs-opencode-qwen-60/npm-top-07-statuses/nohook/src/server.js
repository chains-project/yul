const http = require('http');
const { getStatusPhrase, getAllStatuses, STATUS_CODES } = require('./statusCodes');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  // GET / - List all available status codes
  if (url.pathname === '/' && req.method === 'GET') {
    const statuses = getAllStatuses();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify(statuses, null, 2));
  }

  // GET /codes - Same as root, returns all codes
  if (url.pathname === '/codes' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify(Object.entries(STATUS_CODES), null, 2));
  }

  // GET /lookup/:code - Look up a specific status code
  const lookupMatch = url.pathname.match(/^\/lookup\/(\d+)$/);
  if (lookupMatch) {
    const statusCode = Number(lookupMatch[1]);
    const phrase = getStatusPhrase(statusCode);
    const response = {
      code: statusCode,
      phrase,
      success: phrase !== 'Unknown'
    };

    if (phrase === 'Unknown') {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify(response, null, 2));
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify(response, null, 2));
  }

  // GET /category/:category - Get codes by category (e.g., /category/2xx)
  const categoryMatch = url.pathname.match(/^\/category\/(\d)xx$/);
  if (categoryMatch) {
    const category = `${categoryMatch[1]}xx`;
    const statuses = getAllStatuses().filter(({ code }) => String(code).startsWith(categoryMatch[1]));
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ category: categoryMatch[0], statuses }, null, 2));
  }

  // Return the actual status code and reason phrase
  if (url.pathname.match(/^\/\d{3}$/)) {
    const statusCode = Number(url.pathname.slice(1));
    const phrase = getStatusPhrase(statusCode);

    res.writeHead(statusCode, { 'Content-Type': 'text/plain' });
    return res.end(`${statusCode} ${phrase}`);
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not Found', message: 'Use /lookup/:code to look up a status code' }, null, 2));
});

server.listen(PORT, () => {
  console.log(`HTTP Status Server running on http://localhost:${PORT}`);
  console.log(`Endpoints:`);
  console.log(`  GET /           - List all status codes`);
  console.log(`  GET /codes      - Raw status codes object`);
  console.log(`  GET /lookup/:code - Look up a specific code`);
  console.log(`  GET /category/:category - Get codes by category (e.g., /category/4xx)`);
});