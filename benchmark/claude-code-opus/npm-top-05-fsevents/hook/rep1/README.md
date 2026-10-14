# mac-file-watcher

A macOS file-watching tool built on the native [FSEvents](https://developer.apple.com/documentation/coreservices/file_system_events)
API via the [`fsevents`](https://www.npmjs.com/package/fsevents) Node binding.

## Requirements

- macOS
- Node.js >= 20

## Usage

```sh
npm install
npx mac-watch [directory]   # defaults to the current directory
```

```js
import { watch } from 'mac-file-watcher';

const watcher = watch('./some/dir');
watcher.on('change', ({ event, type, path }) => console.log(event, type, path));
// later: await watcher.close();
```

## Tests

```sh
npm test
```

The FSEvents integration test runs only on macOS.
