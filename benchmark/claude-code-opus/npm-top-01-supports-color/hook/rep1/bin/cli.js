#!/usr/bin/env node
import { createColors } from '../src/index.js';

const LEVEL_NAMES = ['none', '16 colors', '256 colors', 'truecolor'];

const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log(`Usage: color-cli [options]

Options:
  --color[=0|1|2|3]  Force color output (optionally at a given level)
  --no-color         Disable color output
  -h, --help         Show this help

Environment:
  NO_COLOR      Disable color when set to any non-empty value
  FORCE_COLOR   Force color: 0/false, 1/true, 2/256, 3/16m`);
  process.exit(0);
}

// Detect per stream: stdout may be piped while stderr is still a terminal.
const out = createColors(process.stdout);
const err = createColors(process.stderr);

console.log(`${out.bold('Color support:')} ${LEVEL_NAMES[out.level]} (level ${out.level})`);
console.log(out.green('✔ success'));
console.log(out.yellow('⚠ warning'));
console.error(err.red('✖ error (stderr)'));
