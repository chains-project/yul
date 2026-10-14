/**
 * Detach a readable stream from every destination it is piped to.
 *
 * Uses the native `readable.unpipe()` (no argument = all destinations).
 * The stream is left paused so no data is lost after detaching.
 *
 * @param {import('node:stream').Readable} stream
 * @returns {import('node:stream').Readable} the same stream
 */
export function unpipeAll(stream) {
  if (!stream || typeof stream.unpipe !== 'function') {
    throw new TypeError('argument stream must be a readable stream');
  }
  stream.unpipe();
  if (typeof stream.pause === 'function') stream.pause();
  return stream;
}
