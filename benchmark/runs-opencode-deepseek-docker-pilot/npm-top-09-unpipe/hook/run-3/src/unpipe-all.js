function destinationsOf(stream) {
  const state = stream._readableState
  if (!state || !state.pipes) return []
  return Array.isArray(state.pipes) ? state.pipes.slice() : [state.pipes]
}

export function isPiped(stream) {
  return (
    stream !== null &&
    typeof stream === "object" &&
    typeof stream.unpipe === "function" &&
    destinationsOf(stream).length > 0
  )
}

export function unpipeAll(stream) {
  if (
    stream === null ||
    typeof stream !== "object" ||
    typeof stream.unpipe !== "function"
  ) {
    throw new TypeError(
      "unpipeAll expects a readable stream with an unpipe() method"
    )
  }

  const destinations = destinationsOf(stream)

  for (const destination of destinations) {
    stream.unpipe(destination)
  }

  stream.unpipe()

  const remaining = destinationsOf(stream)
  if (remaining.length > 0) {
    throw new Error(
      `unpipeAll was unable to detach ${remaining.length} destination(s)`
    )
  }

  if (typeof stream.pause === "function") {
    stream.pause()
  }

  return destinations
}

export default unpipeAll
