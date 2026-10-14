# mac-fswatch

A macOS file-watching tool built directly on Apple's FSEvents API via the
native [`fsevents`](https://github.com/fsevents/fsevents) binding.

## Requirements

- macOS
- Node.js >= 18

`fsevents` is an optional, darwin-only dependency, so `npm install` won't fail
on other platforms — but the watcher only runs on macOS.

## Usage

```sh
npm install
npx mac-fswatch [dir]     # prints one JSON line per change
```

```js
import { watch } from 'mac-fswatch';

const stop = watch('/some/dir', (e) => {
  // e.event: created | modified | deleted | moved | root-changed | cloned | unknown
  // e.type:  file | directory | symlink
  console.log(e.event, e.type, e.path);
});

await stop();
```

## Tests

```sh
npm test
```
