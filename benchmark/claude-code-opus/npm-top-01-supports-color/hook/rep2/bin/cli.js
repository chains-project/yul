#!/usr/bin/env node
import { getColorLevel } from '../src/color-support.js';
import { stdoutColors as c } from '../src/colors.js';

const LEVEL_NAMES = ['none', 'basic (16)', '256', 'truecolor'];

const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log(`Usage: color-cli [--color | --no-color]

Options:
  --color      Force colored output
  --no-color   Disable colored output
  -h, --help   Show this help

Environment:
  NO_COLOR     Disable color when set to any non-empty value
  FORCE_COLOR  Force color level (0-3)`);
  process.exit(0);
}

const level = getColorLevel();

console.log(c.bold('Color support: ') + LEVEL_NAMES[level]);
console.log(c.green('✔ success'), c.yellow('⚠ warning'), c.red('✖ error'));
console.log(c.dim(c.enabled ? 'Colors enabled.' : 'Colors disabled — printing plain text.'));
