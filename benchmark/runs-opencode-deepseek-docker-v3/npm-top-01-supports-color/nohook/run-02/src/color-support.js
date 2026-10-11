export const LEVEL = {
  NONE: 0,
  BASIC: 1,
  ANSI256: 2,
  TRUECOLOR: 3,
};

function envFlag(name) {
  const value = process.env[name];
  return value !== undefined && value !== '';
}

function forcedLevel() {
  const value = process.env.FORCE_COLOR;
  if (value === undefined) return null;

  if (value === '' || value === '1' || value === 'true') return LEVEL.BASIC;
  if (value === '2') return LEVEL.ANSI256;
  if (value === '3') return LEVEL.TRUECOLOR;
  if (value === '0' || value === 'false') return LEVEL.NONE;

  return LEVEL.BASIC;
}

/**
 * Detect the color level supported by the given stream.
 * Returns one of the LEVEL values: 0 (none), 1 (basic), 2 (256), 3 (truecolor).
 */
export function detectColorLevel(stream = process.stdout) {
  if (envFlag('NO_COLOR')) return LEVEL.NONE;

  const forced = forcedLevel();
  if (forced !== null) return forced;

  if (envFlag('CI')) return LEVEL.NONE;

  if (!stream.isTTY) return LEVEL.NONE;

  const term = process.env.TERM;
  if (term === 'dumb') return LEVEL.NONE;
  if (!term) return LEVEL.NONE;

  const colorterm = process.env.COLORTERM;
  if (colorterm === 'truecolor' || colorterm === '24bit') return LEVEL.TRUECOLOR;
  if (colorterm) return LEVEL.ANSI256;

  if (/-truecolor$/i.test(term)) return LEVEL.TRUECOLOR;
  if (/-256(color)?$/i.test(term)) return LEVEL.ANSI256;

  if (/^screen|^xterm|^vt100|^vt220|^rxvt|color|ansi|cygwin|linux/i.test(term)) {
    return LEVEL.BASIC;
  }

  return LEVEL.BASIC;
}

export function supportsColor(stream = process.stdout) {
  return detectColorLevel(stream) > LEVEL.NONE;
}
