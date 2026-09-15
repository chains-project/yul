const express = require('express');
const fs = require('fs');
const path = require('path');
const unpipe = require('unpipe');

const app = express();
const PORT = process.env.PORT || 3000;

const DATA_FILE = path.join(__dirname, 'data.txt');

app.get('/stream', (req, res) => {
  const source = fs.createReadStream(DATA_FILE);

  source.pipe(res);

  const cleanup = () => {
    // Reliably detach `source` from every destination it's piped to
    // (res, and any other stream that may have piped from it),
    // then stop reading so the file descriptor is released promptly.
    unpipe(source);
    source.destroy();
  };

  source.on('error', cleanup);
  req.on('close', cleanup);
});

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
