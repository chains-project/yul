#!/usr/bin/env node
import process from 'node:process';
import { detectColorSupport, createStyler, CODES } from '../src/color-support.js';

const LEVEL_NAMES = {
  0: 'none',
  1: 'basic (16 colors)',
  2: '256 colors',
  3: 'truecolor (16 million)',
};

function printHelp() {
  const style = createStyler(1);
  process.stdout.write(
    [
      `${style('color-cli', 'green', 'bold')} - detect terminal color support`,
      '',
      `${style('Usage', 'bold')}`,
      '  color-cli [options] [text...]',
      '',
      `${style('Options', 'bold')}`,
      '  --check         Print the detected color support level only',
      '  --color         Force basic color output',
      '  --no-color      Disable colored output',
      '  -h, --help      Show this help',
      '',
      'Environment: NO_COLOR, FORCE_COLOR, TERM, COLORTERM',
      '',
    ].join('\n'),
  );
}

const argv = process.argv.slice(2);
const level = detectColorSupport(process.stdout, process.argv);
const style = createStyler(level);

if (argv.includes('-h') || argv.includes('--help')) {
  printHelp();
  process.exit(0);
}

if (argv.includes('--check')) {
  process.stdout.write(`color support: ${LEVEL_NAMES[level]} (level ${level})\n`);
  process.exit(0);
}

const text = argv.filter((arg) => !arg.startsWith('-')).join(' ') || 'Hello, color world!';

process.stdout.write(`${style(text, 'green', 'bold')}\n`);

if (level === 0) {
  process.stdout.write(
    `${style('(colors disabled)', 'gray')}\n`,
  );
}

export { CODES };
