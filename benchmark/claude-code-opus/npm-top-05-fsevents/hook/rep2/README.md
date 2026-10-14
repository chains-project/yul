# mac-file-watcher

A macOS file-watching tool built on native [FSEvents](https://developer.apple.com/documentation/coreservices/file_system_events) notifications, via the [`fsevents`](https://github.com/fsevents/fsevents) native addon.

## Usage

```sh
npm install
npx mac-file-watcher ~/some/dir
```

Output is tab-separated: `eventId  event  type  path`.

```js
import { watch } from 'mac-file-watcher';

const w = watch('/path/to/dir');
w.on('change', ({ path, event, type, flags, id }) => { /* ... */ });
await w.close();
```

## Notes

- `fsevents` is an `optionalDependency` and only installs on macOS. On other platforms the tool falls back to `fs.watch` (recursive), which gives coarser events with no FSEvents flags or event IDs. This is handy for development and CI but is not the intended runtime.
- FSEvents reports real paths. On macOS `/var` and `/tmp` are symlinks into `/private`, so resolve paths with `realpath` before comparing them.
