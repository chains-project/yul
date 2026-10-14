#!/usr/bin/env node
import { stdoutColors as c, stderrColors as e } from '../src/colors.js';

const args = process.argv.slice(2).filter((a) => !a.startsWith('--color') && a !== '--no-color');

if (args.includes('--help') || args.includes('-h')) {
  console.log(`${c.bold('Usage:')} color-cli [options]

${c.bold('Options:')}
  --color, --color=always   Force colored output
  --no-color, --color=never Disable colored output
  -h, --help                Show this help

Colors are also controlled by the NO_COLOR and FORCE_COLOR env vars.`);
  process.exit(0);
}

console.log(c.green('✔ Success:'), 'everything worked');
console.log(c.yellow('⚠ Warning:'), 'this is a warning');
console.log(c.cyan('ℹ Info:'), `colors are ${c.enabled ? c.bold('enabled') : 'disabled'} on stdout`);
console.error(e.red('✖ Error:'), 'this goes to stderr');
