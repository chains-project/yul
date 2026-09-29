/**
 * Detach every destination currently piped from `readable`.
 *
 * `readable.unpipe()` with no argument detaches all *current* destinations, but
 * a destination can synchronously re-pipe the source from its own `unpipe`
 * handler. That newly attached destination is active again, so a single
 * `unpipe()` call does not guarantee the stream ends up fully detached.
 *
 * Keep draining until no destinations remain. A hard cap turns a destination
 * that re-pipes on every `unpipe` into a loud error instead of an infinite loop.
 *
 * @param {import('node:stream').Readable} readable
 * @param {{ maxPasses?: number }} [options]
 * @returns {number} the number of drain passes performed
 */
export function unpipeAll(readable, { maxPasses = 1000 } = {}) {
  if (!readable || typeof readable.unpipe !== 'function') {
    throw new TypeError('unpipeAll expects a readable stream')
  }

  const state = readable._readableState
  let passes = 0

  for (;;) {
    readable.unpipe()
    passes += 1

    if (!Array.isArray(state?.pipes) || state.pipes.length === 0) {
      return passes
    }

    if (passes >= maxPasses) {
      throw new Error(
        `unpipeAll: destinations kept re-piping after ${maxPasses} attempts`,
      )
    }
  }
}
