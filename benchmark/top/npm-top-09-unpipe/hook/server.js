const express = require('express');
const unpipe = require('unpipe');

const app = express();

// Example: stream a large response body, but stop it from continuing to
// pipe to the response once the client disconnects (or once we decide to
// abort for any other reason). unpipe() detaches a stream from *all* of
// its current destinations in one call, which is more reliable than
// tracking and calling stream.unpipe(dest) for each destination manually.
app.get('/stream', (req, res) => {
  const { PassThrough } = require('stream');
  const source = new PassThrough();

  source.pipe(res);

  const interval = setInterval(() => {
    source.write(`${new Date().toISOString()}\n`);
  }, 1000);

  const stopStreaming = () => {
    clearInterval(interval);
    unpipe(source);
    source.end();
  };

  req.on('close', stopStreaming);
  res.on('error', stopStreaming);
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
