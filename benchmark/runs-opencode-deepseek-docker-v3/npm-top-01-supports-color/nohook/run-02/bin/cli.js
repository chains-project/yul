#!/usr/bin/env node
import { detectColorLevel, LEVEL } from '../src/color-support.js';
import { createStyler } from '../src/ansi.js';

const LEVEL_NAMES = {
  [LEVEL.NONE]: 'none',
  [LEVEL.BASIC]: 'basic (16 colors)',
  [LEVEL.ANSI256]: 'ansi256 (256 colors)',
  [LEVEL.TRUECOLOR]: 'truecolor (16m colors)',
};

function main() {
  const args = process.argv.slice(2);
  const level = detectColorLevel(process.stdout);
  const { style, bold } = createStyler(level);

  if (args.includes('--json')) {
    process.stdout.write(
      JSON.stringify({ supportsColor: level > LEVEL.NONE, level }) + '\n',
    );
    return;
  }

  const text = args.length > 0 ? args.join(' ') : 'Hello, colored world!';

  console.log(`${bold('Terminal color support:')} ${style(LEVEL_NAMES[level], 'cyan')}`);
  console.log(style(text, 'green'));
}

main();
