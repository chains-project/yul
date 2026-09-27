#!/usr/bin/env node
import { rangeStringToRegex, rangeStringToRegExp } from "./index.js";

const [, , range, ...flags] = process.argv;

if (!range || range === "-h" || range === "--help") {
  console.error('Usage: range-regex "1-100" [--no-anchors] [--pad] [-i]');
  process.exit(range ? 0 : 1);
}

try {
  const options = {
    anchors: !flags.includes("--no-anchors"),
    pad: flags.includes("--pad"),
    flags: flags.includes("-i") ? "i" : "",
  };
  const pattern = rangeStringToRegex(range, options);
  const re = rangeStringToRegExp(range, options);
  console.log(pattern);
  console.error(`RegExp: ${re}`);
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
