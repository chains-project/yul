#!/usr/bin/env node
import { expandRange } from "./range.js";

const input = process.argv[2];

if (!input) {
  console.error("Usage: expand-range <range>");
  console.error("Examples:");
  console.error("  expand-range 1-10");
  console.error("  expand-range a-z");
  console.error("  expand-range 0-20:5");
  process.exit(1);
}

try {
  console.log(JSON.stringify(expandRange(input)));
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
