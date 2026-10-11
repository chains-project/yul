#!/usr/bin/env node
import { expandRange } from "./index.js";

const args = process.argv.slice(2);

if (args.length === 0) {
  console.error("Usage: range-expand <range> [<range> ...]");
  console.error("Examples: range-expand 1-10   range-expand a-z");
  process.exit(1);
}

try {
  const values = args.flatMap((arg) => expandRange(arg));
  console.log(values.join(" "));
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
