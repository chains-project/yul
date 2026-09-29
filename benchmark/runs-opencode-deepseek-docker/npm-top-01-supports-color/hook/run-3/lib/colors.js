const CODES = {
  reset: [0, 0],
  bold: [1, 22],
  dim: [2, 22],
  red: [31, 39],
  green: [32, 39],
  yellow: [33, 39],
  blue: [34, 39],
  magenta: [35, 39],
  cyan: [36, 39],
};

export function supportsColor(stream = process.stdout, env = process.env) {
  if (env.FORCE_COLOR === "0") return false;
  if (env.FORCE_COLOR !== undefined && env.FORCE_COLOR !== "") return true;
  if (env.NO_COLOR !== undefined && env.NO_COLOR !== "") return false;

  if (stream && typeof stream.hasColors === "function") {
    return stream.hasColors();
  }

  return Boolean(stream && stream.isTTY);
}

export function colorDepth(stream = process.stdout, env = process.env) {
  if (stream && typeof stream.getColorDepth === "function") {
    return stream.getColorDepth(env);
  }
  return supportsColor(stream, env) ? 4 : 1;
}

export function createPainter({ stream = process.stdout, env = process.env } = {}) {
  const enabled = supportsColor(stream, env);

  const paint = (name, text) => {
    if (!enabled) return String(text);
    const [open, close] = CODES[name] ?? CODES.reset;
    return `\u001b[${open}m${text}\u001b[${close}m`;
  };

  const style = {};
  for (const name of Object.keys(CODES)) {
    style[name] = (text) => paint(name, text);
  }
  style.enabled = enabled;
  return style;
}
