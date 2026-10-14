/**
 * Detect the color level a stream supports.
 *
 * Levels: 0 = none, 1 = 16 colors, 2 = 256 colors, 3 = truecolor (16M).
 *
 * Precedence (highest first):
 *   1. CLI flags: --no-color / --color[=0|1|2|3|256|16m]
 *   2. FORCE_COLOR env var (https://force-color.org)
 *   3. NO_COLOR env var (https://no-color.org) — any non-empty value disables
 *   4. Stream must be a TTY
 *   5. stream.getColorDepth() — Node's built-in TERM/COLORTERM/CI heuristics
 */
export function detectColorLevel(stream = process.stdout, {
  env = process.env,
  argv = process.argv.slice(2),
} = {}) {
  const flagLevel = levelFromFlags(argv);
  if (flagLevel !== undefined) return flagLevel;

  if ('FORCE_COLOR' in env) {
    const forced = parseForceColor(env.FORCE_COLOR);
    if (forced !== undefined) return forced;
  }

  if (env.NO_COLOR) return 0;

  if (!stream || !stream.isTTY) return 0;
  if (env.TERM === 'dumb') return 0;

  if (typeof stream.getColorDepth !== 'function') return 1;
  return depthToLevel(stream.getColorDepth(env));
}

export function supportsColor(stream, options) {
  return detectColorLevel(stream, options) > 0;
}

function levelFromFlags(argv) {
  let level;
  for (const arg of argv) {
    if (arg === '--') break;
    if (arg === '--no-color' || arg === '--no-colors' || arg === '--color=false' || arg === '--color=never') {
      level = 0;
    } else if (arg === '--color' || arg === '--colors' || arg === '--color=true' || arg === '--color=always') {
      level = 1;
    } else if (arg.startsWith('--color=')) {
      const parsed = parseForceColor(arg.slice('--color='.length));
      if (parsed !== undefined) level = parsed;
    }
  }
  return level;
}

function parseForceColor(value) {
  if (value === '' || value === 'true') return 1;
  if (value === 'false') return 0;
  if (value === '256') return 2;
  if (value === '16m' || value === 'truecolor') return 3;
  const n = Number.parseInt(value, 10);
  if (Number.isNaN(n)) return undefined;
  return Math.min(Math.max(n, 0), 3);
}

function depthToLevel(depth) {
  if (depth >= 24) return 3;
  if (depth >= 8) return 2;
  if (depth >= 4) return 1;
  return 0;
}
