#!/usr/bin/env node
import {
	level,
	hasColor,
	hasBasic,
	has256,
	has16m,
	red,
	green,
	yellow,
	cyan,
	bold,
	dim,
} from '../index.js';

const args = process.argv.slice(2);

if (args.includes('--json')) {
	process.stdout.write(
		`${JSON.stringify({level, hasColor, hasBasic, has256, has16m}, null, 2)}\n`,
	);
	process.exit(0);
}

const status = hasColor
	? green(`color enabled (level ${level})`)
	: yellow('color disabled');

process.stdout.write(`${bold('color-cli')} ${dim('>')} ${status}\n`);

if (hasColor) {
	process.stdout.write(`${red('red')} ${green('green')} ${yellow('yellow')} ${cyan('cyan')}\n`);
} else {
	process.stdout.write('This terminal does not support colored output; printing plain text.\n');
}
