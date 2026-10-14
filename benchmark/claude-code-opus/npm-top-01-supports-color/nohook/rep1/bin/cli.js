#!/usr/bin/env node
import { createColors } from '../src/color.js';

const out = createColors(process.stdout);
const err = createColors(process.stderr);

const args = process.argv.slice(2).filter((a) => a !== '--color' && a !== '--no-color');

if (args.includes('--help') || args.includes('-h')) {
  console.log(`Usage: color-cli [--color | --no-color] [name]

Options:
  --color      Force colored output
  --no-color   Disable colored output
  -h, --help   Show this help

Environment:
  NO_COLOR     Disable colored output
  FORCE_COLOR  Force colored output (0 or false to disable)`);
  process.exit(0);
}

const name = args[0] ?? 'world';

console.log(`${out.bold('Hello,')} ${out.green(name)}!`);
console.log(out.gray(`stdout colors: ${out.enabled ? 'on' : 'off'}`));

if (name === 'error') {
  console.error(err.red('Example error message on stderr'));
  process.exitCode = 1;
}
