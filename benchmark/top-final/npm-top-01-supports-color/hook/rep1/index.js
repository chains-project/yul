#!/usr/bin/env node

const supportsColor = require("supports-color");

function paint(text, code) {
  return supportsColor.stdout ? `\x1b[${code}m${text}\x1b[0m` : text;
}

console.log(paint("Success:", 32) + " terminal colors are supported.");
console.log(paint("Warning:", 33) + " this line uses yellow if available.");
console.log(paint("Error:", 31) + " this line uses red if available.");

if (!supportsColor.stdout) {
  console.log("(color output disabled — no color-capable terminal detected)");
}
