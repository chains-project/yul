'use strict';

const { unpipeAll } = require('./unpipe');

/**
 * Pipes a single readable source to many writable destinations while keeping
 * track of exactly which destinations are attached, so they can be removed
 * individually or all at once.
 */
class Broadcast {
  constructor(source) {
    if (!source || typeof source.pipe !== 'function') {
      throw new TypeError('source must be a readable stream');
    }

    this.source = source;
    this.destinations = new Set();
  }

  get size() {
    return this.destinations.size;
  }

  pipe(destination) {
    if (this.destinations.has(destination)) {
      return destination;
    }

    this.destinations.add(destination);

    const forget = () => {
      this.destinations.delete(destination);
    };

    destination.once('finish', forget);
    destination.once('close', forget);
    destination.once('error', () => {
      forget();
      this.source.unpipe(destination);
    });

    this.source.pipe(destination);
    return destination;
  }

  unpipe(destination) {
    if (!this.destinations.delete(destination)) {
      return false;
    }

    this.source.unpipe(destination);
    return true;
  }

  unpipeAll() {
    const targets = Array.from(this.destinations);
    unpipeAll(this.source, targets);
    this.destinations.clear();
    return targets;
  }
}

module.exports = { Broadcast };
