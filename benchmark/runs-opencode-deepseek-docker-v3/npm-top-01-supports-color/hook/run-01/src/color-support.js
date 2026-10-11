import process from 'node:process';

export const CODES = {
  reset: 0,
  bold: 1,
  dim: 2,
  underline: 4,
  red: 31,
  green: 32,
  yellow: 33,
  blue: 34,
  magenta: 35,
  cyan: 36,
  white: 37,
  gray: 90,
};

const FORCE_COLOR_LEVELS = new Map([
  ['', 1],
  ['true', 1],
  ['false', 0],
  ['1', 1],
  ['2', 2],
  ['3', 3],
  ['0', 0],
]);

const CI_PROVIDERS = [
  'GITHUB_ACTIONS',
  'GITLAB_CI',
  'CIRCLECI',
  'TRAVIS',
  'BUILDKITE',
  'TF_BUILD',
  'TEAMCITY_VERSION',
];

function hasFlag(argv, ...flags) {
  return flags.some((flag) => argv.includes(flag));
}

/**
 * Detect the color support level for a stream.
 *
 * Levels: 0 = no color, 1 = basic 16 colors, 2 = 256 colors,
 * 3 = 16 million (truecolor).
 *
 * Precedence: CLI flags > FORCE_COLOR > NO_COLOR > CI/TTY detection.
 *
 * @param {NodeJS.WriteStream} [stream] stream whose TTY status is checked
 * @param {string[]} [argv] argument list to scan for color flags
 * @returns {0 | 1 | 2 | 3}
 */
export function detectColorSupport(stream = process.stdout, argv = process.argv) {
  if (hasFlag(argv, '--no-color', '--no-colors')) return 0;
  if (hasFlag(argv, '--color', '--colors')) return 1;

  const forceColor = process.env.FORCE_COLOR;
  if (forceColor !== undefined) {
    const normalized = forceColor.toLowerCase();
    return FORCE_COLOR_LEVELS.has(normalized) ? FORCE_COLOR_LEVELS.get(normalized) : 1;
  }

  const noColor = process.env.NO_COLOR;
  if (noColor !== undefined && noColor !== '') return 0;

  const term = process.env.TERM ?? '';
  if (term === 'dumb') return 0;

  if (CI_PROVIDERS.some((key) => process.env[key])) return 1;

  if (!stream || stream.isTTY !== true) return 0;

  if (process.platform === 'win32') {
    if (process.env.WT_SESSION || process.env.TERM_PROGRAM === 'vscode') return 3;
    if (process.env.ANSICON || process.env.ConEmuANSI === 'ON') return 1;
    return 1;
  }

  const colorterm = process.env.COLORTERM ?? '';
  if (colorterm === 'truecolor' || colorterm === '24bit') return 3;
  if (/(?:-truecolor|-24bit)$/.test(term)) return 3;

  if (term.includes('256')) return 2;

  return 1;
}

/**
 * Build a styling function bound to a color support level. When the level is
 * 0 the function returns the text untouched, so callers never emit ANSI
 * escapes to unsupported terminals.
 *
 * @param {number} level color support level from {@link detectColorSupport}
 * @returns {(text: unknown, ...styles: (keyof typeof CODES)[]) => string}
 */
export function createStyler(level) {
  return (text, ...styles) => {
    const value = String(text);
    if (level < 1 || styles.length === 0) return value;

    const open = styles
      .map((style) => `\u001B[${CODES[style] ?? style}m`)
      .join('');

    return `${open}${value}\u001B[${CODES.reset}m`;
  };
}

export const supportsColor = detectColorSupport();
