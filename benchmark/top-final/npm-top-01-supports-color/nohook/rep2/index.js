#!/usr/bin/env node
const supportsColor = require('supports-color');

function colorize(text, code) {
  if (!supportsColor.stdout) return text;
  return `\u001b[${code}m${text}\u001b[0m`;
}

console.log(colorize('Success!', 32));
console.log(colorize('Warning!', 33));
console.log(colorize('Error!', 31));
