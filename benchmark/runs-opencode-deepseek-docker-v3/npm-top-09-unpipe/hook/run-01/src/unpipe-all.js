import unpipe from "unpipe";

const tracked = new WeakMap();

function destinationsOf(source) {
  const destinations = new Set(tracked.get(source) ?? []);
  const pipes = source?._readableState?.pipes;

  if (Array.isArray(pipes)) {
    for (const destination of pipes) destinations.add(destination);
  } else if (pipes) {
    destinations.add(pipes);
  }

  return destinations;
}

export function pipeTo(source, destination, options) {
  let destinations = tracked.get(source);
  if (!destinations) {
    destinations = new Set();
    tracked.set(source, destinations);
  }
  destinations.add(destination);
  return source.pipe(destination, options);
}

export function unpipeAll(source) {
  if (!source) throw new TypeError("source stream is required");

  const destinations = destinationsOf(source);

  unpipe(source);

  for (const destination of destinations) {
    if (typeof source.unpipe === "function") source.unpipe(destination);
  }

  tracked.delete(source);
  return source;
}

export function destinations(source) {
  return [...destinationsOf(source)];
}
