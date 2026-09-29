const CODES = {
  bold: [1, 22],
  red: [31, 39],
  green: [32, 39],
  yellow: [33, 39],
  blue: [34, 39],
};

const FORCE_COLOR_RE = /^(true|yes|on)$/i;

function parseForceColor(value) {
  if (value === 'false' || value === '0') return 0;
  if (value === '' || FORCE_COLOR_RE.test(value)) return 1;

  const parsed = Number.parseInt(value, 10);
  if (Number.isNaN(parsed)) return 1;

  return Math.min(Math.max(parsed, 0), 3);
}

export function detectColorLevel({ stream = process.stdout, env = process.env } = {}) {
  if (env.FORCE_COLOR !== undefined) return parseForceColor(env.FORCE_COLOR);

  if (env.NO_COLOR) return 0;

  if (env.TERM === 'dumb') return 0;

  if (!stream || !stream.isTTY) return 0;

  if (typeof stream.getColorDepth === 'function') {
    return stream.getColorDepth(env);
  }

  if (env.COLORTERM === 'truecolor' || env.COLORTERM === '24bit') return 3;
  if (/(256|truecolor|24bit)/i.test(env.TERM || '')) return 2;

  return 1;
}

export function createColors(level = detectColorLevel()) {
  const depth = Number.isInteger(level) ? level : 0;

  const paint = (style, text) => {
    const code = CODES[style];
    if (!code || depth < 1) return String(text);
    return `\u001B[${code[0]}m${text}\u001B[${code[1]}m`;
  };

  return {
    level: depth,
    enabled: depth > 0,
    bold: (text) => paint('bold', text),
    red: (text) => paint('red', text),
    green: (text) => paint('green', text),
    yellow: (text) => paint('yellow', text),
    blue: (text) => paint('blue', text),
  };
}

export const colors = createColors();
