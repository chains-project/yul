# fs-watch-mac

A macOS file-watching tool built on [fsevents](https://www.npmjs.com/package/fsevents), Node's native binding to the macOS FSEvents API for low-level filesystem change notifications.

## Requirements

- macOS (fsevents is a Darwin-only native module)
- Node.js >= 14

## Install

```sh
npm install
```

## Usage

```sh
npm start -- /path/to/watch
```

Or use the library directly:

```js
const { watch } = require('fs-watch-mac');

const stop = watch('/path/to/watch', (path, flags, info) => {
  console.log(path, flags, info);
});

// later
await stop();
```
