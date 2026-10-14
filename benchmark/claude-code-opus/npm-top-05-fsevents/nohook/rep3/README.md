# mac-fswatch

macOS file-watching tool built on [`fsevents`](https://github.com/fsevents/fsevents),
the native Node binding to Apple's FSEvents API. Watches are recursive and
kernel-driven — no polling, no per-file descriptors.

## Requirements

- macOS (the `fsevents` addon only builds/installs on darwin)
- Node.js 18+

## Usage

```sh
npm install
npm start -- ~/some/dir          # human-readable output
npm start -- ~/some/dir --json   # one JSON event per line
npm test
```

As a library:

```js
import { watch } from 'mac-fswatch';

const stop = watch('/path/to/dir', (e) => {
  console.log(e.event, e.type, e.path, e.id);
});
// later: await stop();
```

Each event includes the decoded `event` (`created`, `modified`, `deleted`,
`moved`, …), `type` (`file`, `directory`, `symlink`), `changes` (inode,
finder, access, xattrs), the raw `flags` bitmask, and the FSEvents event `id`.

## Notes

- FSEvents coalesces rapid changes and reports canonical paths
  (e.g. `/private/var/...` instead of `/var/...`).
- `fsevents.constants` is re-exported as `constants` for raw flag checks.
