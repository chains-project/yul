#!/usr/bin/env node

/**
 * A CLI tool that detects terminal color support before printing colored text.
 * Uses the `supports-color` package to check if the terminal can display colors.
 */

// Check if the terminal supports color, including the `--color` flag override
const colorSupport = require('supports-color');

if (colorSupport) {
  // colorSupport has a `level` property:
  //   0 = no color support
  //   1 = basic color support (16 colors)
  //   2 = 256 color support
  //   3 = true color support (16 million colors)

  const level = colorSupport.level;
  console.log('Color level:', level);

  // Determine which ANSI color codes to use based on support level
  const colors = {
    red: level >= 1 ? '\x1B[31m' : '',
    green: level >= 1 ? '\x1B[32m' : '',
    yellow: level >= 1 ? '\x1B[33m' : '',
    blue: level >= 1 ? '\x1B[34m' : '',
    magenta: level >= 2 ? '\x1B[35m' : '',
    cyan: level >= 2 ? '\x1B[36m' : '',
    white: level >= 1 ? '\x1B[37m' : '',
    bold: level >= 1 ? '\x1B[1m' : '',
    underline: level >= 1 ? '\x1B[4m' : '',
    reset: '\x1B[0m',
    bgRed: level >= 2 ? '\x1B[41m' : '',
    bgGreen: level >= 2 ? '\x1B[42m' : '',
    bgBlue: level >= 2 ? '\x1B[44m' : '',
  };

  // True color (16M) escape codes
  const trueColor = level >= 3;

  console.log('');
  console.log(colors.bold + '=== Color Support Test ===' + colors.reset);
  console.log('');

  // Test basic foreground colors (level >= 1)
  if (level >= 1) {
    console.log('Basic colors (16 colors):');
    console.log(colors.red + '  Red text' + colors.reset);
    console.log(colors.green + '  Green text' + colors.reset);
    console.log(colors.yellow + '  Yellow text' + colors.reset);
    console.log(colors.blue + '  Blue text' + colors.reset);
    console.log(colors.magenta + '  Magenta text' + colors.reset);
    console.log(colors.cyan + '  Cyan text' + colors.reset);
    console.log(colors.white + '  White text' + colors.reset);
    console.log(colors.bold + '  Bold text' + colors.reset);
    console.log(colors.underline + '  Underlined text' + colors.reset);
    console.log('');
  }

  // Test background colors (level >= 2)
  if (level >= 2) {
    console.log('Background colors (256 colors):');
    console.log(colors.bgRed + '  Red background' + colors.reset);
    console.log(colors.bgGreen + '  Green background' + colors.reset);
    console.log(colors.bgBlue + '  Blue background' + colors.reset);
    console.log('');
  }

  // Test true color (level >= 3)
  if (trueColor) {
    console.log('True color (16 million colors):');
    // Simple true color gradient demonstration
    for (let i = 0; i < 5; i++) {
      // Green to red gradient using true color
      const r = Math.round(255 * i / 4);
      const g = Math.round(255 * (4 - i) / 4);
      const b = 0;
      const color = `\x1B[38;2;${r};${g};${b}m`;
      const bg = `\x1B[48;2;${b};${g};${r}m`;
      console.log(colors.bold + `  ${color}RGB(${r},${g},${b}) - Gradient block` + colors.reset);
      console.log(`  ${bg}RGB(${b},${g},${r}) - Reverse gradient block` + colors.reset);
    }
    console.log('');
  }

  // Information about the color support
  console.log('--- Color Support Details ---');
  console.log('Has basic color support:', level >= 1);
  console.log('Has 256 color support:', level >= 2);
  console.log('Has true color support:', trueColor);
  console.log('Stream supports color:', colorSupport.stdout ? 'yes' : 'no');
  console.log('Environment flags:', colorSupport.stdout && colorSupport.stdout.hasBasic ? 'basic' : colorSupport.stdout && colorSupport.stdout.has256 ? '256' : colorSupport.stdout && colorSupport.stdout.has16m ? 'truecolor' : 'none');
  console.log('');

  // Demonstrate colored output with a summary
  if (level === 0) {
    console.log(colors.bold + 'No color support detected. Use --color flag to force color output.' + colors.reset);
  } else if (level === 1) {
    console.log(colors.bold + colors.green + 'Terminal supports basic (16) colors.' + colors.reset);
  } else if (level === 2) {
    console.log(colors.bold + colors.blue + 'Terminal supports 256 colors.' + colors.reset);
  } else {
    console.log(colors.bold + colors.cyan + 'Terminal supports true color (16 million colors)!'+ colors.reset);
  }

} else {
  // colorSupport is falsy - no color support at all
  console.log('No color support detected in this terminal.');
  console.log('Use the --color flag to force color output if needed.');
  console.log('');
  console.log('Example usage:');
  console.log('  node cli.js --color        # Force color output');
  console.log('  node cli.js                # Auto-detect terminal capabilities');
}