# color-cli

A dependency-free Node.js CLI that checks whether the terminal supports color before printing colored text.

## Usage

```sh
npm start -- Alice          # colored if stdout is a color-capable TTY
node bin/cli.js | cat       # piped: plain text
NO_COLOR=1 node bin/cli.js  # plain text
FORCE_COLOR=1 node bin/cli.js | cat   # colored even when piped
node bin/cli.js --no-color  # plain text
```

## How detection works (`src/color.js`)

Checks run in this order, and the first match wins:

1. `--no-color` / `--color` flags
2. `FORCE_COLOR` (enables color; `0` or `false` disables it)
3. `NO_COLOR` set to a non-empty value disables color ([no-color.org](https://no-color.org))
4. `TERM=dumb` disables color
5. Output that isn't a TTY (piped or redirected) gets no color
6. Otherwise, Node's `tty.WriteStream#hasColors()` decides, based on TERM, COLORTERM, CI, and Windows version

stdout and stderr are checked separately, so `cli 2>err.log` still colors stdout.

## Tests

```sh
npm test
```
