'use strict'

/**
 * Detach a readable stream from every destination it is piped to.
 *
 * Modern streams: `unpipe()` with no argument removes all destinations.
 * Legacy (pre-streams2) streams have no `unpipe`; `Stream#pipe` registers a
 * `close` listener named `cleanup` on the source for each destination, and
 * calling it removes that pipe's listeners.
 */
function unpipe (stream) {
  if (!stream) {
    throw new TypeError('argument stream is required')
  }

  if (typeof stream.unpipe === 'function') {
    stream.unpipe()
    return
  }

  if (!hasPipeDataListeners(stream)) {
    return
  }

  for (const listener of stream.listeners('close')) {
    if (listener.name === 'cleanup') {
      listener.call(stream)
    }
  }
}

function hasPipeDataListeners (stream) {
  return stream.listeners('data').some((listener) => listener.name === 'ondata')
}

module.exports = unpipe
