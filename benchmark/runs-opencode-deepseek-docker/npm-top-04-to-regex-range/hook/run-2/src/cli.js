#!/usr/bin/env node
import process from "node:process";
import { parseRange, rangeToRegex } from "./range-to-regex.js";

function usage() {
  return [
    "Usage: range-to-regex <range> [flags]",
    "",
    "  <range>  a numeric range such as 1-100, or a single number like 42",
    "  [flags]  optional RegExp flags (e.g. i)",
    "",
    "Prints the regular expression that matches any number in the range.",
  ].join("\n");
}

function main(argv) {
  const [range, flags = ""] = argv;

  if (!range || range === "-h" || range === "--help") {
    console.log(usage());
    process.exitCode = range ? 0 : 1;
    return;
  }

  try {
    const [min, max] = parseRange(range);
    console.log(rangeToRegex(min, max, flags).toString());
  } catch (error) {
    console.error(`error: ${error.message}`);
    console.error(usage());
    process.exitCode = 1;
  }
}

main(process.argv.slice(2));
