#!/usr/bin/env node
import { rangeToRegex, rangeToRegexSource } from "../src/index.js";

const args = process.argv.slice(2);

if (args.length === 0 || args.includes("-h") || args.includes("--help")) {
  console.log("Usage: range-to-regex <range> [--source]");
  console.log("  range-to-regex 1-100");
  console.log("  range-to-regex --source 1-100");
  process.exit(args.length === 0 ? 1 : 0);
}

const sourceOnly = args.includes("--source");
const range = args.find((arg) => !arg.startsWith("--"));

try {
  if (sourceOnly) {
    console.log(rangeToRegexSource(range));
  } else {
    console.log(rangeToRegex(range));
  }
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
