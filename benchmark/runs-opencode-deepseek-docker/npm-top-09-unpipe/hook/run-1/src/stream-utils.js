/**
 * Returns every destination currently piped from `state`, normalised to an
 * array. Node stores a single pipe directly and multiple pipes as an array.
 */
function destinationsOf(state) {
  if (!state || !state.pipes) return []
  return Array.isArray(state.pipes) ? [...state.pipes] : [state.pipes]
}

/**
 * Reliably detaches a readable stream from *all* of its destinations.
 *
 * Node's `readable.unpipe()` with no argument detaches every destination, but
 * it iterates the live `state.pipes` collection. If an `'unpipe'` listener (or
 * a `'close'`/`'end'` handler) adds a new pipe while we are tearing down, that
 * destination can survive the call. This helper repeatedly snapshots and
 * detaches destinations until the pipes collection is empty, then falls back
 * to Node's no-argument `unpipe()` as a final backstop.
 *
 * @param {import('node:stream').Readable} source
 * @returns {import('node:stream').Readable} the same source, for chaining
 */
export function unpipeAll(source) {
  if (!source || typeof source.unpipe !== 'function') {
    throw new TypeError('unpipeAll requires a Readable stream')
  }

  const state = source._readableState

  // Bound the retries so a listener that perpetually re-pipes cannot spin
  // forever; 1024 passes is far more than any legitimate fan-out.
  let passes = 0
  while (destinationsOf(state).length > 0 && passes < 1024) {
    for (const destination of destinationsOf(state)) {
      source.unpipe(destination)
    }
    passes += 1
  }

  // Backstop for any destination Node tracks that we could not see above.
  source.unpipe()

  return source
}

export default unpipeAll
