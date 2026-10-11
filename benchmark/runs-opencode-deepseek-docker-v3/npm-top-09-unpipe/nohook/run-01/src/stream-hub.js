'use strict'

const unpipe = require('unpipe')

class StreamHub {
  constructor(source) {
    if (!source || typeof source.pipe !== 'function') {
      throw new TypeError('StreamHub requires a readable source stream')
    }

    this.source = source
    this.destinations = new Set()
  }

  add(destination) {
    if (!destination || typeof destination.write !== 'function') {
      throw new TypeError('destination must be a writable stream')
    }

    this.destinations.add(destination)
    this.source.pipe(destination)
    return destination
  }

  remove(destination) {
    this.destinations.delete(destination)
    this.source.unpipe(destination)
    return destination
  }

  removeAll() {
    // `unpipe(source)` detaches the source from *every* destination Node knows
    // about, including pipes that were not registered through this hub.
    unpipe(this.source)
    this.destinations.clear()
  }
}

module.exports = StreamHub
