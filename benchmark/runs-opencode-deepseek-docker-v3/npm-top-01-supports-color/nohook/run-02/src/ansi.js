import { LEVEL } from './color-support.js';

const CODES = {
  reset: 0,
  bold: 1,
  red: 31,
  green: 32,
  yellow: 33,
  blue: 34,
  magenta: 35,
  cyan: 36,
};

const FG_256 = {
  red: 196,
  green: 46,
  yellow: 226,
  blue: 21,
  magenta: 201,
  cyan: 51,
};

const FG_RGB = {
  red: [255, 85, 85],
  green: [80, 250, 123],
  yellow: [241, 250, 140],
  blue: [98, 114, 164],
  magenta: [255, 121, 198],
  cyan: [139, 233, 253],
};

const noColor = (text) => text;

export function createStyler(level) {
  if (level <= LEVEL.NONE) {
    return { level, color: noColor, bold: noColor, style: noColor };
  }

  const style = (text, ...names) => {
    const codes = names
      .map((name) => {
        if (name === 'bold') return '1';
        if (level >= LEVEL.TRUECOLOR && FG_RGB[name]) {
          const [r, g, b] = FG_RGB[name];
          return `38;2;${r};${g};${b}`;
        }
        if (level >= LEVEL.ANSI256 && FG_256[name]) {
          return `38;5;${FG_256[name]}`;
        }
        if (CODES[name] !== undefined) return String(CODES[name]);
        return null;
      })
      .filter(Boolean);

    if (codes.length === 0) return text;
    return `\u001b[${codes.join(';')}m${text}\u001b[${CODES.reset}m`;
  };

  return {
    level,
    style,
    color: (text, name) => style(text, name),
    bold: (text) => style(text, 'bold'),
  };
}
