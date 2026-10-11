import parcelWatcher from '@parcel/watcher';

export const EVENT_TYPES = Object.freeze(['create', 'update', 'delete']);

function normalize(event) {
  return {
    type: event.type,
    path: event.path,
  };
}

export async function watch(directory, onEvents, options = {}) {
  if (typeof onEvents !== 'function') {
    throw new TypeError('onEvents must be a function');
  }

  const subscription = await parcelWatcher.subscribe(
    directory,
    (error, events) => {
      if (error) {
        onEvents(error, []);
        return;
      }
      onEvents(null, events.map(normalize));
    },
    options,
  );

  return subscription;
}

export function writeSnapshot(directory, snapshotPath, options = {}) {
  return parcelWatcher.writeSnapshot(directory, snapshotPath, options);
}

export function getEventsSince(directory, snapshotPath, options = {}) {
  return parcelWatcher.getEventsSince(directory, snapshotPath, options);
}
