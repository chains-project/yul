#!/usr/bin/env node
import { colorSupport, colorEnabled, describeColorSupport } from '../src/color-support.js';
import { bold, dim, red, green, yellow, blue, cyan } from '../src/colors.js';

const level = colorEnabled ? colorSupport.level : 0;
const name = describeColorSupport();

console.log(`${bold(cyan('colorful-cli'))} — terminal color support`);
console.log(`  detection: ${green(name)} (level ${level})`);

if (colorEnabled) {
  console.log(
    `  ${red('red')} ${green('green')} ${yellow('yellow')} ${blue('blue')} ${cyan('cyan')} ${bold('bold')} ${dim('dim')}`,
  );
} else {
  console.log(
    dim('  Colors are disabled (piped output, NO_COLOR, or an unsupported terminal).'),
  );
}
