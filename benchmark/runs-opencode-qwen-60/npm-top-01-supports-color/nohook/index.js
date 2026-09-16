#!/usr/bin/env node

'use strict';

const supportsColor = require('supports-color');

// Use the appropriate ANSI color codes only if the terminal supports them
if (supportsColor.stdout) {
  // eslint-disable-next-line no-undef
  console.log('\x1b[32mThis text is green\x1b[0m');
  console.log('\x1b[31mThis text is red\x1b[0m');
  console.log('\x1b[33mThis text is yellow\x1b[0m');
  console.log('\x1b[34mThis text is blue\x1b[0m');
  console.log('\x1b[35mThis text is magenta\x1b[0m');
  console.log('\x1b[36mThis text is cyan\x1b[0m');
  console.log(`\nTerminal color support: level ${supportsColor.stdout.level}`);
} else {
  console.log('This terminal does not support colored output.');
  console.log('No colors will be displayed.');
}