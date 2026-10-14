# color-cli

A zero-dependency Node.js CLI that detects whether the terminal supports
colored output before printing ANSI colors.

```sh
npm link          # or: npm start
color-cli
color-cli | cat   # piped → plain text
NO_COLOR=1 color-cli
FORCE_COLOR=3 color-cli | cat
```

## Detection rules

Highest precedence first:

1. `--no-color` / `--color` flags
2. `NO_COLOR` (non-empty) disables color — see https://no-color.org
3. `FORCE_COLOR` sets the level (`0`–`3`, `true`, `false`)
4. Non-TTY output (pipes, files) → no color
5. `TERM=dumb` → no color
6. Otherwise Node's `tty.WriteStream#getColorDepth()` decides
   (handles `TERM`, `COLORTERM`, CI providers, Windows)

## Usage in code

```js
import { stdoutColors as c, getColorLevel } from './src/index.js';
console.log(c.green('ok'));   // plain "ok" when color is unsupported
```

stdout and stderr are detected independently, so `cli 2>err.log` still
colors stdout.

## Test

```sh
npm test
```
