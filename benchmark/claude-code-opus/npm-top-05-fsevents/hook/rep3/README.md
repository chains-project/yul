# mac-fswatch

macOS file-watching tool built on native [FSEvents](https://developer.apple.com/documentation/coreservices/file_system_events)
via the [`fsevents`](https://github.com/fsevents/fsevents) N-API binding. macOS only.

## Usage

```sh
npm install
npm start -- ~/some/dir          # human-readable output
npm start -- --json ~/some/dir   # one JSON object per event
```

As a library:

```js
import { watch } from 'mac-fswatch';

const watcher = watch('/path/to/dir', (e) => {
  // e: { path, event, type, flags, id, changes: { inode, finder, access, xattrs } }
  console.log(e.event, e.path);
});

await watcher.stop();
```

Pass `{ since: <eventId> }` to replay events from FSEvents history starting at a previous event ID.

## Tests

```sh
npm test
```

The event test runs only on macOS; on other platforms it is skipped.
