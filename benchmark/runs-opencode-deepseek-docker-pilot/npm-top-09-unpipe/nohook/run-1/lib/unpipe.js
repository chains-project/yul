'use strict'

/*
 * Based on the `unpipe` module.
 * Copyright(c) 2015 Douglas Christopher Wilson
 * MIT Licensed
 */

/**
 * Determine if there are Node.js pipe-like data listeners.
 */

function hasPipeDataListeners (stream) {
  const listeners = stream.listeners('data')

  for (let i = 0; i < listeners.length; i++) {
    if (listeners[i].name === 'ondata') {
      return true
    }
  }

  return false
}

/**
 * Unpipe a stream from all of its destinations.
 *
 * Prefers the native `stream.unpipe()`, which detaches every destination
 * tracked by the source. Falls back to the legacy close-listener cleanup
 * used by old-style (pre-0.10) streams that do not expose `unpipe`.
 *
 * @param {object} stream
 * @returns {object} the same stream
 * @public
 */

function unpipe (stream) {
  if (!stream) {
    throw new TypeError('argument stream is required')
  }

  if (typeof stream.unpipe === 'function') {
    stream.unpipe()
    return stream
  }

  if (!hasPipeDataListeners(stream)) {
    return stream
  }

  const listeners = stream.listeners('close')

  for (let i = 0; i < listeners.length; i++) {
    const listener = listeners[i]

    if (listener.name !== 'cleanup' && listener.name !== 'onclose') {
      continue
    }

    listener.call(stream)
  }

  return stream
}

module.exports = unpipe
