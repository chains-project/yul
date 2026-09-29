'use strict';

function toArray(destinations) {
  if (!destinations) {
    return [];
  }

  if (Array.isArray(destinations)) {
    return destinations.slice();
  }

  if (typeof destinations[Symbol.iterator] === 'function') {
    return Array.from(destinations);
  }

  return [destinations];
}

/**
 * Reliably detach `source` from all of its destinations.
 *
 * `Readable#unpipe()` called without an argument is the supported way to
 * detach every destination, and it keeps working after a destination has
 * closed. Passing the known `destinations` as well makes the call safe for
 * custom stream implementations whose `unpipe()` only understands an explicit
 * destination. Streams without an `unpipe()` method fall back to emitting
 * `'unpipe'` on each destination.
 *
 * @param {import('stream').Readable} source
 * @param {Iterable<import('stream').Writable>} [destinations]
 * @returns {Array<import('stream').Writable>} the destinations that were detached
 */
function unpipeAll(source, destinations) {
  if (!source || typeof source.pipe !== 'function') {
    throw new TypeError('source must be a readable stream');
  }

  const targets = toArray(destinations);

  if (typeof source.unpipe === 'function') {
    for (const destination of targets) {
      source.unpipe(destination);
    }

    // Authoritative cleanup: this detaches *every* destination, including any
    // that were piped without being tracked, and is harmless to repeat.
    source.unpipe();
  } else {
    for (const destination of targets) {
      destination.emit('unpipe', source);
    }
  }

  return targets;
}

module.exports = { unpipeAll };
