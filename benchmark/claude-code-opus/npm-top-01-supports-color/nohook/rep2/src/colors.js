import { supportsColor } from './supports-color.js';

const STYLES = {
  bold: [1, 22],
  dim: [2, 22],
  red: [31, 39],
  green: [32, 39],
  yellow: [33, 39],
  blue: [34, 39],
  magenta: [35, 39],
  cyan: [36, 39],
  gray: [90, 39],
};

/**
 * Build a set of style functions. When `enabled` is false every function
 * returns its input unchanged, so callers never need to branch themselves.
 */
export function createColors(enabled) {
  const colors = { enabled };
  for (const [name, [open, close]] of Object.entries(STYLES)) {
    colors[name] = enabled
      ? (text) => `\x1b[${open}m${text}\x1b[${close}m`
      : (text) => String(text);
  }
  return colors;
}

// Detected separately: stdout may be piped while stderr is still a terminal.
export const stdoutColors = createColors(supportsColor(process.stdout));
export const stderrColors = createColors(supportsColor(process.stderr));
