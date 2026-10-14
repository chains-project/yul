import { detectColorLevel } from './color-support.js';

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
 * Create color helpers bound to a stream. When the stream doesn't support
 * color, every helper returns its input unchanged.
 */
export function createColors(stream = process.stdout, options) {
  const level = detectColorLevel(stream, options);
  const enabled = level > 0;
  const colors = { level, enabled };

  for (const [name, [open, close]] of Object.entries(CODES)) {
    colors[name] = enabled
      ? (text) => `\x1b[${open}m${text}\x1b[${close}m`
      : (text) => String(text);
  }
  return colors;
}
