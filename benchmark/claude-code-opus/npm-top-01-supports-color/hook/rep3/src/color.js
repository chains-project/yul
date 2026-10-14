/**
 * Detect how many colors a stream supports.
 * Returns 0 (none), 16, 256, or 16777216 (truecolor).
 *
 * Precedence (highest first):
 *   1. CLI flags: --no-color / --color[=0|1|2|3]
 *   2. FORCE_COLOR env var (https://force-color.org)
 *   3. NO_COLOR env var (https://no-color.org)
 *   4. Non-TTY stream or TERM=dumb -> no color
 *   5. Node's built-in stream.getColorDepth()
 */
const LEVELS = [0, 16, 256, 16777216];

export function colorDepth(stream = process.stdout, { env = process.env, argv = process.argv } = {}) {
  if (argv.includes('--no-color') || argv.includes('--color=false')) return 0;
  const flag = argv.find((a) => a === '--color' || a.startsWith('--color='));
  if (flag) return levelFrom(flag.split('=')[1] ?? '1');

  if ('FORCE_COLOR' in env) return levelFrom(env.FORCE_COLOR);
  if (env.NO_COLOR) return 0;

  if (!stream?.isTTY || env.TERM === 'dumb') return 0;
  return typeof stream.getColorDepth === 'function' ? 2 ** stream.getColorDepth(env) : 16;
}

function levelFrom(value) {
  if (value === '' || value === 'true') return 16;
  if (value === 'false') return 0;
  const n = Number.parseInt(value, 10);
  return Number.isNaN(n) ? 16 : LEVELS[Math.min(Math.max(n, 0), 3)];
}

export function supportsColor(stream, opts) {
  return colorDepth(stream, opts) > 0;
}

/** Build color helpers bound to a stream; they become no-ops when color is unsupported. */
export function createColors(stream = process.stdout, opts) {
  const enabled = supportsColor(stream, opts);
  const wrap = (open, close) => (text) => (enabled ? `\x1b[${open}m${text}\x1b[${close}m` : String(text));
  return {
    enabled,
    bold: wrap(1, 22),
    dim: wrap(2, 22),
    red: wrap(31, 39),
    green: wrap(32, 39),
    yellow: wrap(33, 39),
    blue: wrap(34, 39),
    cyan: wrap(36, 39),
  };
}
