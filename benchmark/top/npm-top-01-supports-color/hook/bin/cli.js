#!/usr/bin/env node
import supportsColor from "supports-color";

const RESET = "\x1b[0m";
const GREEN = "\x1b[32m";
const RED = "\x1b[31m";

function colorize(text, code) {
  return supportsColor.stdout ? `${code}${text}${RESET}` : text;
}

const message = process.argv.slice(2).join(" ") || "Hello from colorcheck-cli!";

if (supportsColor.stdout) {
  console.log(colorize(message, GREEN));
  console.log(colorize(`Color support: ${JSON.stringify(supportsColor.stdout)}`, RED));
} else {
  console.log(message);
  console.log("Color support: none detected");
}
