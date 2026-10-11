import process from 'node:process';
import supportsColor from 'supports-color';

const EXPLICIT_COLOR_FLAG =
  /^--(?:color|colors)(?:=(?:true|false|always|never|16m|256|full|truecolor))?$|^--no-colou?rs?$/;
function hasExplicitColorFlag(argv) {
  return argv.some((arg) => EXPLICIT_COLOR_FLAG.test(arg));
}

// `supports-color` accounts for TTY detection, TERM/COLORTERM capabilities,
// `--color`/`--no-color` flags, FORCE_COLOR and CI environments. It does not
// honor NO_COLOR, so the CLI resolves that here.
export function resolveColorSupport({ detected, env = {}, argv = [] }) {
  // An explicit CLI flag or FORCE_COLOR always wins over NO_COLOR.
  if ('FORCE_COLOR' in env || hasExplicitColorFlag(argv)) {
    return detected;
  }

  // Honor the NO_COLOR standard (https://no-color.org).
  if ('NO_COLOR' in env && env.NO_COLOR !== '') {
    return false;
  }

  return detected;
}

export const colorSupport = resolveColorSupport({
  detected: supportsColor.stdout ?? false,
  env: process.env,
  argv: process.argv,
});

export const colorEnabled = Boolean(colorSupport);

export function describeColorSupport(support = colorSupport) {
  if (!support) {
    return 'none';
  }

  if (support.has16m) {
    return 'truecolor (16m)';
  }

  if (support.has256) {
    return '256 colors';
  }

  if (support.hasBasic) {
    return 'basic (16 colors)';
  }

  return 'none';
}
