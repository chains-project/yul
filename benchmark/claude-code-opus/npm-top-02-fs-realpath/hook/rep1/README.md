# canonical-path

Resolve all symlinks in a path to its real, canonical absolute path.

```sh
npx canonical-path ./some/link        # CLI
npm test
```

```js
import { realpath, realpathSync } from 'canonical-path';
await realpath('./some/link');
```

Both functions use Node's native realpath (`fs.realpathSync.native` /
`fs.promises.realpath`, i.e. the OS's own `realpath(3)`), so sync and async
results match each other and stay the same across Node versions. Node's JS
`fs.realpath` is used only as a fallback when the native call fails for
reasons other than a missing path, symlink loop, or permission error.

Requires Node >= 18. No dependencies.
