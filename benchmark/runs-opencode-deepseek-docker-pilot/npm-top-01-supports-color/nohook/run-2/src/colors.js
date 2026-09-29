import { ColorLevel } from "./supports-color.js";

const ESC = "\u001b[";

const CODES = {
  reset: [0, 0],
  bold: [1, 22],
  dim: [2, 22],
  italic: [3, 23],
  underline: [4, 24],
  inverse: [7, 27],
  hidden: [8, 28],
  strikethrough: [9, 29],
  black: [30, 39],
  red: [31, 39],
  green: [32, 39],
  yellow: [33, 39],
  blue: [34, 39],
  magenta: [35, 39],
  cyan: [36, 39],
  white: [37, 39],
  gray: [90, 39],
  brightRed: [91, 39],
  brightGreen: [92, 39],
  brightYellow: [93, 39],
  brightBlue: [94, 39],
  brightMagenta: [95, 39],
  brightCyan: [96, 39],
  brightWhite: [97, 39],
};

/**
 * Build a set of text formatters for the given color level.
 *
 * When the level is `ColorLevel.NONE` every formatter is an identity function,
 * so it is always safe to call them without branching at the call site.
 *
 * @param {number} level one of the `ColorLevel` values
 * @returns {Record<string, Function>}
 */
export function createColors(level = ColorLevel.NONE) {
  const enabled = level > ColorLevel.NONE;
  const make = (open, close) => (text) => {
    const value = String(text);
    if (!enabled || value === "") return value;
    return `${ESC}${open}m${value}${ESC}${close}m`;
  };

  const colors = {};
  for (const [name, [open, close]] of Object.entries(CODES)) {
    colors[name] = make(open, close);
  }

  colors.rgb = (r, g, b, text) => {
    const value = String(text);
    if (!enabled || level < ColorLevel.TRUECOLOR || value === "") return value;
    return `${ESC}38;2;${r};${g};${b}m${value}${ESC}39m`;
  };

  colors.ansi256 = (code, text) => {
    const value = String(text);
    if (!enabled || level < ColorLevel.COLORS_256 || value === "") return value;
    return `${ESC}38;5;${code}m${value}${ESC}39m`;
  };

  colors.level = level;
  colors.enabled = enabled;
  return colors;
}
