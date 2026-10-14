/**
 * Detach a readable stream from every destination it is piped to.
 *
 * Calling `readable.unpipe()` with no arguments removes all pipe
 * destinations, cleans up the listeners `pipe()` installed, emits
 * 'unpipe' on each destination, and leaves the source paused.
 *
 * @param {import('node:stream').Readable} stream
 * @returns {import('node:stream').Readable} the same stream, for chaining
 */
export function unpipeAll(stream) {
  if (!stream || typeof stream.unpipe !== 'function') {
    throw new TypeError('argument stream must be a readable stream');
  }

  stream.unpipe();
  return stream;
}
