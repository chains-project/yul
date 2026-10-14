/**
 * Detach a readable stream from every destination it is piped to.
 *
 * Uses the native `readable.unpipe()` (no argument = all destinations).
 * Throws if no stream is given. Safe to call on non-readables, destroyed
 * streams, or streams with no pipes.
 *
 * @param {import('node:stream').Readable} stream
 * @returns {import('node:stream').Readable} the same stream
 */
export function unpipe(stream) {
  if (!stream) {
    throw new TypeError('argument stream is required');
  }
  if (typeof stream.unpipe === 'function') {
    stream.unpipe();
  }
  return stream;
}
