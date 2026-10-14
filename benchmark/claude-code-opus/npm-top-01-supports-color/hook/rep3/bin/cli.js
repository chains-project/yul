#!/usr/bin/env node
import { colorDepth, createColors } from '../src/color.js';

const out = createColors(process.stdout);
const err = createColors(process.stderr);

if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log(`Usage: color-cli [--color[=0-3]] [--no-color]

Environment:
  NO_COLOR      Disable color when set to a non-empty value
  FORCE_COLOR   Force color level (0-3), overrides NO_COLOR and TTY detection`);
  process.exit(0);
}

console.log(out.bold('Color support check'));
console.log(`  stdout: ${colorDepth(process.stdout)} colors`);
console.log(`  stderr: ${colorDepth(process.stderr)} colors`);
console.log(out.green('✔ success'), out.yellow('⚠ warning'), out.cyan('ℹ info'));
console.error(err.red('✖ error output (stderr)'));
