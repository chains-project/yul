# color-cli

A dependency-free Node.js CLI that checks whether the terminal supports color before printing colored text.

## Usage

```sh
npm start                             # sample output, colored if supported
node bin/cli.js --no-color            # turn color off
NO_COLOR=1 node bin/cli.js            # turn color off
FORCE_COLOR=3 node bin/cli.js | cat   # force truecolor even when piped
npm test
```

## How detection works

Detection runs separately for each stream (stdout and stderr), in this order:

1. `--no-color` / `--color[=level]` flags
2. `FORCE_COLOR` ([force-color.org](https://force-color.org))
3. `NO_COLOR` ([no-color.org](https://no-color.org))
4. Stream must be a TTY, and `TERM` must not be `dumb`
5. Node's `stream.getColorDepth()` (checks `TERM`, `COLORTERM`, CI providers, Windows version, etc.)

Levels: `0` none, `1` 16 colors, `2` 256 colors, `3` truecolor.

```js
import { createColors, supportsColor } from './src/index.js';

const c = createColors(process.stdout);
console.log(c.green('ok'));   // plain "ok" when color isn't supported
```
