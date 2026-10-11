import process from "node:process";
import { getColorSupport } from "./color-support.js";

const CODES = {
  reset: [0, 0],
  bold: [1, 22],
  dim: [2, 22],
  italic: [3, 23],
  underline: [4, 24],
  red: [31, 39],
  green: [32, 39],
  yellow: [33, 39],
  blue: [34, 39],
  magenta: [35, 39],
  cyan: [36, 39],
  white: [37, 39],
  gray: [90, 39],
  redBright: [91, 39],
  greenBright: [92, 39],
  yellowBright: [93, 39],
  blueBright: [94, 39],
  magentaBright: [95, 39],
  cyanBright: [96, 39],
  whiteBright: [97, 39],
};

function applyStyle(name, text, support) {
  const code = CODES[name];
  if (!code || !support.supported) {
    return String(text);
  }
  return `\u001B[${code[0]}m${text}\u001B[${code[1]}m`;
}

function createColors(stream = process.stdout, options = {}) {
  const support = getColorSupport(stream, options);
  const colors = { support };

  for (const name of Object.keys(CODES)) {
    colors[name] = (text) => applyStyle(name, text, support);
  }

  return colors;
}

export { createColors, getColorSupport };
export { supportsColor } from "./color-support.js";
