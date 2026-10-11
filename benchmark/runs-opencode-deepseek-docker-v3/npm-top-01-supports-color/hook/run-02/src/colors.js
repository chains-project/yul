import { colorEnabled } from './color-support.js';

const codes = {
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

function wrap(open, close, text) {
  return colorEnabled ? `\u001B[${open}m${text}\u001B[${close}m` : `${text}`;
}

export const { bold, dim, red, green, yellow, blue, magenta, cyan } =
  Object.fromEntries(
    Object.entries(codes).map(([name, [open, close]]) => [
      name,
      (text) => wrap(open, close, text),
    ]),
  );
