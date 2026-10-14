// Detects whether a given output stream can render ANSI colors.
//
// Precedence (highest first):
//   1. --no-color / --color CLI flags
//   2. NO_COLOR (https://no-color.org) — any non-empty value disables color
//   3. FORCE_COLOR — "0"/"false" disables; "1"/"2"/"3"/"true"/"" enables
//   4. Non-TTY streams (pipes, files) get no color
//   5. Node's built-in tty detection (TERM, COLORTERM, CI, Windows, etc.)

/** @typedef {0 | 1 | 2 | 3} ColorLevel  0 = none, 1 = 16 colors, 2 = 256, 3 = truecolor */

const DEPTH_TO_LEVEL = { 1: 0, 4: 1, 8: 2, 24: 3 };

function forceColorLevel(value) {
  if (value === undefined) return undefined;
  if (value === '' || value === 'true') return 1;
  if (value === 'false') return 0;
  const n = Number.parseInt(value, 10);
  if (Number.isNaN(n)) return undefined;
  return /** @type {ColorLevel} */ (Math.min(Math.max(n, 0), 3));
}

/**
 * @param {object} [options]
 * @param {NodeJS.WriteStream} [options.stream=process.stdout]
 * @param {NodeJS.ProcessEnv} [options.env=process.env]
 * @param {string[]} [options.argv=process.argv]
 * @returns {ColorLevel}
 */
export function getColorLevel({
  stream = process.stdout,
  env = process.env,
  argv = process.argv,
} = {}) {
  if (argv.includes('--no-color')) return 0;
  if (argv.includes('--color')) return 1;

  if (env.NO_COLOR) return 0;

  const forced = forceColorLevel(env.FORCE_COLOR);
  if (forced !== undefined) return forced;

  if (!stream?.isTTY) return 0;
  if (env.TERM === 'dumb') return 0;

  if (typeof stream.getColorDepth === 'function') {
    return DEPTH_TO_LEVEL[stream.getColorDepth(env)] ?? 0;
  }
  return 1;
}

/** @returns {boolean} */
export function supportsColor(options) {
  return getColorLevel(options) > 0;
}
