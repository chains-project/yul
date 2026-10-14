/**
 * Decide whether `stream` should receive ANSI color codes.
 *
 * Precedence (first match wins):
 *   1. CLI flags:   --no-color / --color=never  -> off
 *                   --color / --color=always    -> on
 *   2. NO_COLOR (any non-empty value, see https://no-color.org) -> off
 *      NODE_DISABLE_COLORS (any non-empty value)                -> off
 *   3. FORCE_COLOR: "0" or "false" -> off, any other value -> on
 *   4. Stream is not a TTY (piped / redirected to a file) -> off
 *   5. TERM=dumb -> off
 *   6. Otherwise defer to Node's own terminal capability check
 *      (tty.WriteStream#hasColors, which inspects TERM, COLORTERM, CI, OS).
 *
 * `env` and `argv` are injectable so the logic is easy to test.
 */
export function supportsColor(
  stream = process.stdout,
  { env = process.env, argv = process.argv } = {},
) {
  const flag = colorFlag(argv);
  if (flag !== undefined) return flag;

  if (env.NO_COLOR || env.NODE_DISABLE_COLORS) return false;

  if (env.FORCE_COLOR !== undefined) {
    return !['0', 'false'].includes(env.FORCE_COLOR.toLowerCase());
  }

  if (!stream || !stream.isTTY) return false;

  if (env.TERM === 'dumb') return false;

  if (typeof stream.hasColors === 'function') {
    return stream.hasColors(env);
  }

  return true;
}

function colorFlag(argv) {
  let result;
  // Last flag wins, so `--color --no-color` disables colors.
  for (const arg of argv) {
    if (arg === '--no-color' || arg === '--color=never') result = false;
    else if (arg === '--color' || arg === '--color=always') result = true;
  }
  return result;
}
