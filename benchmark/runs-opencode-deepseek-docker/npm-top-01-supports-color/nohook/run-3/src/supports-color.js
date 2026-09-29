import process from 'node:process';

const COLOR_FLAGS = new Set(['--color', '--colors', '--colour', '--colours']);
const NO_COLOR_FLAGS = new Set([
  '--no-color',
  '--no-colors',
  '--no-colour',
  '--no-colours',
]);

function levelFromFlags(argv) {
  if (argv.some((arg) => NO_COLOR_FLAGS.has(arg))) return 0;
  if (argv.some((arg) => COLOR_FLAGS.has(arg))) return 1;
  return undefined;
}

function levelFromEnv(env) {
  const forced = env.FORCE_COLOR;
  if (forced !== undefined) {
    if (forced === '' || forced === 'true') return 1;
    if (forced === 'false') return 0;
    const parsed = Number.parseInt(forced, 10);
    return Number.isNaN(parsed) ? 1 : Math.min(Math.max(parsed, 0), 3);
  }

  if (env.NO_COLOR !== undefined && env.NO_COLOR !== '') return 0;

  return undefined;
}

function levelFromStream(stream, env) {
  if (!stream || !stream.isTTY) return 0;
  if (env.TERM === 'dumb') return 0;

  if (process.platform === 'win32') {
    if (env.CI) return 1;
    if (env.WT_SESSION || env.ANSICON || env.TERM_PROGRAM === 'vscode') return 3;
    return 1;
  }

  if (/truecolor|24bit/i.test(env.COLORTERM || '')) return 3;
  if (/256color/i.test(env.TERM || '')) return 2;
  return 1;
}

/**
 * Returns the color support level for a stream:
 *   0 = none, 1 = 16 colors, 2 = 256 colors, 3 = truecolor.
 */
export function detectColorLevel(
  stream = process.stdout,
  env = process.env,
  argv = process.argv.slice(2),
) {
  return levelFromFlags(argv) ?? levelFromEnv(env) ?? levelFromStream(stream, env);
}

export const supportsColor = {
  stdout: detectColorLevel(process.stdout),
  stderr: detectColorLevel(process.stderr),
};
