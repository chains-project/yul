const TRACKER = Symbol('unpipe.tracker')

function isStream(value) {
  return value !== null && typeof value === 'object' && typeof value.pipe === 'function'
}

function trackerOf(readable) {
  return readable[TRACKER]
}

export function trackDestinations(readable) {
  if (!isStream(readable)) {
    throw new TypeError('trackDestinations expects a readable stream')
  }
  if (trackerOf(readable)) return trackerOf(readable)

  const destinations = new Set()
  const originalPipe = readable.pipe
  const originalUnpipe = readable.unpipe

  const onUnpipe = (_source, destination) => {
    if (destination) destinations.delete(destination)
    else destinations.clear()
  }

  readable.on('unpipe', onUnpipe)

  readable.pipe = function patchedPipe(destination, options) {
    const result = originalPipe.call(this, destination, options)
    if (isStream(destination)) {
      destinations.add(destination)
      const drop = () => destinations.delete(destination)
      destination.once('close', drop)
      destination.once('finish', drop)
      destination.once('error', drop)
    }
    return result
  }

  const tracker = {
    get destinations() {
      return [...destinations]
    },
    get size() {
      return destinations.size
    },
    unpipeAll() {
      originalUnpipe.call(readable)
      destinations.clear()
      return readable
    },
    stopTracking() {
      readable.off('unpipe', onUnpipe)
      readable.pipe = originalPipe
      delete readable[TRACKER]
    },
  }

  Object.defineProperty(readable, TRACKER, {
    value: tracker,
    configurable: true,
  })

  return tracker
}

export function unpipeAll(readable) {
  if (!isStream(readable)) {
    throw new TypeError('unpipeAll expects a readable stream')
  }

  const tracker = trackerOf(readable)
  if (tracker) {
    tracker.unpipeAll()
  } else {
    readable.unpipe()
  }

  return readable
}
