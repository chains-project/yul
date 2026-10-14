'use strict';

/**
 * Detach `stream` from every destination it is piped to.
 *
 * Modern streams (stream.Readable) support `unpipe()` with no arguments,
 * which removes all destinations at once. Legacy streams (old-style
 * `Stream.prototype.pipe`) have no `unpipe`; for those, pipe() registers a
 * 'close' listener named `cleanup` per destination, so we invoke those to
 * tear down each pipe's listeners.
 *
 * @param {import('stream').Stream} stream
 * @returns {import('stream').Stream} the same stream, for chaining
 */
function unpipeAll(stream) {
  if (!stream) {
    throw new TypeError('argument stream is required');
  }

  if (typeof stream.unpipe === 'function') {
    stream.unpipe();
    return stream;
  }

  if (typeof stream.listeners !== 'function') {
    return stream;
  }

  // Legacy streams: only proceed if pipe-installed 'data' handlers exist.
  const hasPipeDataListener = stream
    .listeners('data')
    .some((listener) => listener.name === 'ondata');
  if (!hasPipeDataListener) {
    return stream;
  }

  for (const listener of stream.listeners('close')) {
    if (listener.name === 'cleanup') {
      listener.call(stream);
    }
  }

  return stream;
}

module.exports = { unpipeAll };
