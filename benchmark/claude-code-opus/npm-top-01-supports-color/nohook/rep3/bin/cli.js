#!/usr/bin/env node
import { supportsColor, createColors } from '../src/color.js';

const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log(`Usage: color-cli [options]

Options:
  --color      Force colored output
  --no-color   Disable colored output
  -h, --help   Show this help

Environment:
  NO_COLOR     Disable colored output when set to a non-empty value
  FORCE_COLOR  Force colored output (FORCE_COLOR=0 disables)`);
  process.exit(0);
}

const out = createColors(supportsColor({ stream: process.stdout }));
const err = createColors(supportsColor({ stream: process.stderr }));

console.log(out.green('✔ Success:'), 'everything worked');
console.log(out.yellow('⚠ Warning:'), 'something to look at');
console.log(out.cyan('ℹ Info:'), out.dim('extra details'));
console.error(err.red('✖ Error:'), 'example message on stderr');
