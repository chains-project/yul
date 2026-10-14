# fswatch-macos

A macOS file-watching tool using native FSEvents via [`fsevents`](https://github.com/fsevents/fsevents).

## Usage

```sh
npm install
npx fswatch-macos [path]   # prints one JSON line per filesystem event
```

```js
const { watch } = require('fswatch-macos');
const stop = watch('/some/dir', (e) => console.log(e.event, e.path));
// later: await stop();
```

`fsevents` is an optional dependency so `npm install` won't fail on Linux/CI; `watch()` throws there.
