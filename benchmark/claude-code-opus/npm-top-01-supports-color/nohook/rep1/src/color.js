/**
 * Terminal color support detection, using Node's built-in tty APIs plus the
 * common conventions:
 *   - `--no-color` / `--color` CLI flags (highest priority)
 *   - NO_COLOR (https://no-color.org) disables color
 *   - FORCE_COLOR enables color, even when output is piped (`0`/`false` disables)
 *   - TERM=dumb disables color
 *   - Output that is not a TTY (piped/redirected) gets no color by default
 */

const ANSI = {
  bold: 1,
  dim: 2,
  red: 31,
  green: 32,
  yellow: 33,
  blue: 34,
  magenta: 35,
  cyan: 36,
  gray: 90,
};

/**
 * @param {NodeJS.WriteStream} [stream]
 * @param {{ argv?: string[], env?: NodeJS.ProcessEnv }} [options]
 * @returns {boolean}
 */
export function supportsColor(
  stream = process.stdout,
  { argv = process.argv, env = process.env } = {},
) {
  if (argv.includes('--no-color')) return false;
  if (argv.includes('--color')) return true;

  if ('FORCE_COLOR' in env) {
    return !['0', 'false'].includes(env.FORCE_COLOR);
  }
  if ('NO_COLOR' in env && env.NO_COLOR !== '') return false;
  if (env.TERM === 'dumb') return false;

  if (!stream?.isTTY) return false;

  // tty.WriteStream#hasColors() inspects TERM, COLORTERM, CI vars, Windows
  // version, etc. Pass env explicitly so the injected env is honored.
  if (typeof stream.hasColors === 'function') {
    return stream.hasColors(env);
  }
  return true;
}

/**
 * Build a set of color functions bound to a stream. When the stream doesn't
 * support color, every function returns its input unchanged.
 *
 * @param {NodeJS.WriteStream} [stream]
 * @param {{ argv?: string[], env?: NodeJS.ProcessEnv, enabled?: boolean }} [options]
 */
export function createColors(stream = process.stdout, options = {}) {
  const enabled = options.enabled ?? supportsColor(stream, options);
  const colors = { enabled };
  for (const [name, code] of Object.entries(ANSI)) {
    const close = name === 'bold' || name === 'dim' ? 22 : 39;
    colors[name] = enabled
      ? (text) => `\x1b[${code}m${text}\x1b[${close}m`
      : (text) => String(text);
  }
  return colors;
}
