const { unpipe } = require('unpipe');

function createHookedStream(stream) {
  const destinations = new Set();
  const hooks = {
    beforeUnpipe: [],
    afterUnpipe: [],
    onError: []
  };

  const originalPipe = stream.pipe.bind(stream);
  stream.pipe = function (dest, options) {
    destinations.add(dest);
    return originalPipe(dest, options);
  };

  const originalUnpipe = stream.unpipe.bind(stream);
  stream.unpipe = function (dest) {
    try {
      for (const hook of hooks.beforeUnpipe) {
        hook(dest || 'all');
      }

      if (dest) {
        destinations.delete(dest);
        return originalUnpipe(dest);
      }

      for (const d of [...destinations]) {
        originalUnpipe(d);
      }
      destinations.clear();
      return stream;
    } catch (err) {
      for (const hook of hooks.onError) {
        hook(err);
      }
      throw err;
    } finally {
      for (const hook of hooks.afterUnpipe) {
        hook(dest || 'all');
      }
    }
  };

  stream.hookBeforeUnpipe = (fn) => { hooks.beforeUnpipe.push(fn); return stream; };
  stream.hookAfterUnpipe = (fn) => { hooks.afterUnpipe.push(fn); return stream; };
  stream.hookOnError = (fn) => { hooks.onError.push(fn); return stream; };

  stream.ensureUnpiped = function () {
    destinations.clear();
    return unpipe(stream);
  };

  return stream;
}

module.exports = { createHookedStream };