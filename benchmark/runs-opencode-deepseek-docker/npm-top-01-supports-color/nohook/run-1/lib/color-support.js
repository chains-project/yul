export const LEVELS = Object.freeze({
  NONE: 0,
  BASIC: 1,
  ANSI256: 2,
  TRUECOLOR: 3,
});

const CI_ENV_VARS = [
  'GITHUB_ACTIONS',
  'GITLAB_CI',
  'CIRCLECI',
  'TRAVIS',
  'BUILDKITE',
  'TEAMCITY_VERSION',
  'TF_BUILD',
  'JENKINS_URL',
];

function flag(argv, names) {
  return argv.some((arg) => names.includes(arg));
}

function ciName(env) {
  return CI_ENV_VARS.find((name) => env[name]);
}

function isFalsy(value) {
  return value === '0' || /^false$/i.test(value);
}

export function detectColorSupport({
  stream = process.stdout,
  env = process.env,
  argv = process.argv.slice(2),
} = {}) {
  if (env.FORCE_COLOR !== undefined && env.FORCE_COLOR !== '') {
    switch (env.FORCE_COLOR) {
      case '0':
      case 'false':
        return { level: LEVELS.NONE, reason: 'FORCE_COLOR=0' };
      case '2':
        return { level: LEVELS.ANSI256, reason: 'FORCE_COLOR=2' };
      case '3':
      case 'truecolor':
        return { level: LEVELS.TRUECOLOR, reason: 'FORCE_COLOR=3' };
      default:
        return { level: LEVELS.BASIC, reason: `FORCE_COLOR=${env.FORCE_COLOR}` };
    }
  }

  if (flag(argv, ['--no-color', '--no-colors', '--color=false', '--color=never'])) {
    return { level: LEVELS.NONE, reason: 'disabled by CLI flag' };
  }

  if (flag(argv, ['--color', '--colors', '--color=true', '--color=always'])) {
    return { level: LEVELS.BASIC, reason: 'enabled by CLI flag' };
  }

  if (env.NO_COLOR) {
    return { level: LEVELS.NONE, reason: 'NO_COLOR is set' };
  }

  if (env.TERM === 'dumb') {
    return { level: LEVELS.NONE, reason: 'TERM=dumb' };
  }

  const isTTY = Boolean(stream && stream.isTTY);
  const inCI = env.CI && !isFalsy(env.CI);

  if (!isTTY && !inCI) {
    return { level: LEVELS.NONE, reason: 'output is not a TTY' };
  }

  if (!isTTY && inCI) {
    return { level: LEVELS.BASIC, reason: `CI environment (${ciName(env) || 'CI'})` };
  }

  if (process.platform === 'win32' && !isModernWindowsTerminal(env)) {
    return { level: LEVELS.NONE, reason: 'legacy Windows console' };
  }

  if (!env.TERM) {
    return { level: LEVELS.NONE, reason: 'TERM is not set' };
  }

  if (env.COLORTERM === 'truecolor' || env.COLORTERM === '24bit') {
    return { level: LEVELS.TRUECOLOR, reason: `COLORTERM=${env.COLORTERM}` };
  }

  if (/-256(color)?$/i.test(env.TERM) || /256color/i.test(env.TERM)) {
    return { level: LEVELS.ANSI256, reason: `TERM=${env.TERM}` };
  }

  return { level: LEVELS.BASIC, reason: `TERM=${env.TERM}` };
}

function isModernWindowsTerminal(env) {
  return Boolean(env.WT_SESSION || env.ANSICON || env.ConEmuANSI === 'ON' || env.TERM_PROGRAM);
}

export function supportsColor(options) {
  return detectColorSupport(options).level > LEVELS.NONE;
}

const FOREGROUND = {
  black: 30,
  red: 31,
  green: 32,
  yellow: 33,
  blue: 34,
  magenta: 35,
  cyan: 36,
  white: 37,
  gray: 90,
};

export function createColors(level = LEVELS.NONE) {
  const wrap = (open) => (text) =>
    level > LEVELS.NONE ? `\u001B[${open}m${text}\u001B[0m` : String(text);

  const colors = { level };
  for (const [name, code] of Object.entries(FOREGROUND)) {
    colors[name] = wrap(code);
  }
  colors.bold = wrap(1);
  colors.underline = wrap(4);
  colors.rgb = (r, g, b) => (text) => {
    if (level < LEVELS.TRUECOLOR) {
      return String(text);
    }
    return `\u001B[38;2;${r};${g};${b}m${text}\u001B[0m`;
  };

  return colors;
}
