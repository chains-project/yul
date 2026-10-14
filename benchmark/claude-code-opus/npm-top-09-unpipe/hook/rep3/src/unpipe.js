'use strict'

/**
 * Unpipe a stream from all of its destinations.
 *
 * Works with modern Readable streams (which expose `unpipe()`) and with
 * legacy streams piped via the classic `Stream.prototype.pipe`, which has no
 * `unpipe()` and instead registers a `cleanup` listener per destination on
 * the source's `close` event.
 *
 * @param {import('stream').Stream} stream
 */
function unpipe (stream) {
  if (!stream) {
    throw new TypeError('argument stream is required')
  }

  if (typeof stream.unpipe === 'function') {
    // With no destination argument, this detaches every piped destination.
    stream.unpipe()
    return
  }

  // Legacy stream: nothing to do unless it is actually piped somewhere.
  if (!stream.listeners('data').some((l) => l.name === 'ondata')) {
    return
  }

  // listeners() returns a copy, so cleanup removing itself is safe here.
  for (const listener of stream.listeners('close')) {
    if (listener.name === 'cleanup') {
      listener.call(stream)
    }
  }
}

module.exports = unpipe
