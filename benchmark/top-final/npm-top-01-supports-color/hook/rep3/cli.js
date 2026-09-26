#!/usr/bin/env node
import supportsColor from "supports-color";

const message = process.argv.slice(2).join(" ") || "Hello, world!";

function colorize(text) {
  if (!supportsColor.stdout) return text;
  return `\x1b[32m${text}\x1b[0m`;
}

console.log(colorize(message));
