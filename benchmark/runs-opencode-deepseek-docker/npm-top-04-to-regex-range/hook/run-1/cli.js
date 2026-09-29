#!/usr/bin/env node
import process from "node:process";
import { rangeToRegex, parseRange } from "./index.js";

const USAGE = `Usage: range-to-regex <min-max> [options]

Convert a numeric range into a single regular expression.

Options:
  --no-anchor   Print the pattern without the ^...$ anchors
  -h, --help    Show this help message

Examples:
  range-to-regex 1-100
  range-to-regex 0-255 --no-anchor
`;

function main(argv) {
  const args = argv.slice(2);

  if (args.includes("-h") || args.includes("--help")) {
    process.stdout.write(USAGE);
    return 0;
  }
  if (args.length === 0) {
    process.stderr.write(USAGE);
    return 1;
  }

  const anchor = !args.includes("--no-anchor");
  const rangeArg = args.find((arg) => !arg.startsWith("-"));
  if (!rangeArg) {
    process.stderr.write(`error: missing numeric range\n\n${USAGE}`);
    return 1;
  }

  try {
    const [min, max] = parseRange(rangeArg);
    process.stdout.write(`${rangeToRegex(min, max, { anchor })}\n`);
    return 0;
  } catch (error) {
    process.stderr.write(`error: ${error.message}\n`);
    return 1;
  }
}

process.exitCode = main(process.argv);
