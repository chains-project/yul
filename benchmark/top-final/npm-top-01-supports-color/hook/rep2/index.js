#!/usr/bin/env node

import supportsColor from 'supports-color'

function colorize(text, code) {
  if (!supportsColor.stdout) return text
  return `\u001b[${code}m${text}\u001b[0m`
}

const message = process.argv.slice(2).join(' ') || 'Hello, world!'

console.log(colorize(message, '32'))
