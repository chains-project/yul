#!/usr/bin/env node
import supportsColor from "supports-color";

const message = process.argv.slice(2).join(" ") || "Hello, world!";

if (supportsColor.stdout) {
  console.log(`\u001b[32m${message}\u001b[0m`);
} else {
  console.log(message);
}
