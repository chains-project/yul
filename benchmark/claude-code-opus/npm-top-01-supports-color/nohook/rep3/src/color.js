// Terminal color detection with no dependencies.
//
// Precedence (highest first):
//   1. --color / --no-color CLI flags
//   2. FORCE_COLOR env var (FORCE_COLOR=0 disables, any other value enables)
//   3. NO_COLOR env var (any non-empty value disables; see https://no-color.org)
//   4. Whether the stream is a TTY whose terminal reports color support
//      (Node's tty.WriteStream#hasColors, which also checks TERM, CI, etc.)

/**
 * Decide whether colored output should be written to `stream`.
 *
 * @param {object} [options]
 * @param {NodeJS.WriteStream} [options.stream=process.stdout]
 * @param {NodeJS.ProcessEnv} [options.env=process.env]
 * @param {string[]} [options.argv=process.argv]
 * @returns {boolean}
 */
export function supportsColor({
  stream = process.stdout,
  env = process.env,
  argv = process.argv,
} = {}) {
  if (argv.includes('--no-color')) return false;
  if (argv.includes('--color')) return true;

  if ('FORCE_COLOR' in env) {
    return env.FORCE_COLOR !== '0' && env.FORCE_COLOR !== 'false';
  }
  if (env.NO_COLOR) return false;

  // Piped or redirected output (files, `| less`, CI logs) is not a TTY.
  if (!stream?.isTTY || typeof stream.hasColors !== 'function') return false;

  return stream.hasColors(env);
}

const CODES = {
  bold: [1, 22],
  dim: [2, 22],
  red: [31, 39],
  green: [32, 39],
  yellow: [33, 39],
  blue: [34, 39],
  cyan: [36, 39],
  gray: [90, 39],
};

/**
 * Create a set of color functions. When color is disabled each function
 * returns its input unchanged, so callers never need to branch.
 *
 * @param {boolean} enabled
 * @returns {Record<keyof typeof CODES, (text: string) => string>}
 */
export function createColors(enabled) {
  const colors = {};
  for (const [name, [open, close]] of Object.entries(CODES)) {
    colors[name] = enabled
      ? (text) => `\x1b[${open}m${text}\x1b[${close}m`
      : (text) => String(text);
  }
  return colors;
}
