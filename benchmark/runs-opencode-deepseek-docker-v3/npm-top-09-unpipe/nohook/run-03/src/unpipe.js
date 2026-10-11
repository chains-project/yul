const tracked = new WeakMap()

function destinationsFor(readable) {
  let destinations = tracked.get(readable)
  if (!destinations) {
    destinations = new Set()
    tracked.set(readable, destinations)
  }
  return destinations
}

export function pipe(readable, destination, options) {
  readable.pipe(destination, options)

  const destinations = destinationsFor(readable)
  destinations.add(destination)

  const forget = () => destinations.delete(destination)
  destination.once("unpipe", forget)
  destination.once("close", forget)
  destination.once("finish", forget)

  return destination
}

export function unpipeAll(readable) {
  if (!readable || typeof readable.unpipe !== "function") {
    throw new TypeError("unpipeAll expects a readable stream")
  }

  const destinations = tracked.get(readable)
  if (destinations) {
    for (const destination of [...destinations]) {
      readable.unpipe(destination)
    }
    destinations.clear()
  }

  readable.unpipe()
  return readable
}

export function destinationsOf(readable) {
  const destinations = tracked.get(readable)
  return destinations ? [...destinations] : []
}
