import { supportsColor } from './color-support.js';

const CODES = {
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
 * Build a palette of color functions. When color is unsupported, every
 * function returns its input unchanged, so callers never need to branch.
 *
 * @param {boolean} [enabled]
 */
export function createColors(enabled = supportsColor()) {
  const colors = { enabled };
  for (const [name, [open, close]] of Object.entries(CODES)) {
    colors[name] = enabled
      ? (text) => `\x1b[${open}m${text}\x1b[${close}m`
      : (text) => String(text);
  }
  return colors;
}

export const stdoutColors = createColors(supportsColor({ stream: process.stdout }));
export const stderrColors = createColors(supportsColor({ stream: process.stderr }));
