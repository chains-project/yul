#!/usr/bin/env node
import supportsColor from 'supports-color';

const message = process.argv.slice(2).join(' ') || 'Hello, world!';

function colorize(text) {
  if (!supportsColor.stdout) return text;
  return `\u001B[32m${text}\u001B[39m`;
}

console.log(colorize(message));
