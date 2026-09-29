const ANSI = {
  reset: 0,
  bold: 1,
  dim: 2,
  italic: 3,
  underline: 4,
  red: 31,
  green: 32,
  yellow: 33,
  blue: 34,
  magenta: 35,
  cyan: 36,
  white: 37,
  gray: 90,
};

/**
 * Determine the color level supported by `stream`.
 *
 * 0 = no color, 1 = 16 colors, 2 = 256 colors, 3 = truecolor (16m).
 *
 * Honors the `NO_COLOR` and `FORCE_COLOR` environment conventions and falls
 * back to the terminal's own TTY / color-depth detection.
 */
export function colorLevel(stream = process.stdout) {
  const { FORCE_COLOR, NO_COLOR, TERM } = process.env;

  if (NO_COLOR !== undefined && NO_COLOR !== '') return 0;

  if (FORCE_COLOR !== undefined && FORCE_COLOR !== '') {
    const n = Number.parseInt(FORCE_COLOR, 10);
    if (Number.isNaN(n) || n <= 0) return 0;
    if (n === 1) return 1;
    if (n === 2) return 2;
    return 3;
  }

  if (!stream || !stream.isTTY) return 0;
  if (TERM === 'dumb') return 0;

  if (typeof stream.getColorDepth === 'function') {
    const depth = stream.getColorDepth();
    if (depth >= 24) return 3;
    if (depth >= 8) return 2;
    if (depth >= 4) return 1;
    return 0;
  }

  if (typeof stream.hasColors === 'function' && stream.hasColors()) return 1;
  return 0;
}

export function supportsColor(stream = process.stdout) {
  return colorLevel(stream) > 0;
}

/**
 * Build a set of color helpers bound to `stream`. When the terminal does not
 * support color every helper becomes an identity function, so callers never
 * need to branch on `enabled` themselves.
 */
export function createColors(stream = process.stdout) {
  const level = colorLevel(stream);
  const enabled = level > 0;

  const wrap = (code) => (text) =>
    enabled ? `\x1b[${code}m${text}\x1b[${ANSI.reset}m` : String(text);

  const colors = { enabled, level };
  for (const [name, code] of Object.entries(ANSI)) {
    if (name === 'reset') continue;
    colors[name] = wrap(code);
  }
  return colors;
}

export default createColors();
