#!/usr/bin/env node
import { expandRange } from "./index.js";

const [, , range, ...rest] = process.argv;
const step = rest.length > 0 ? Number(rest[0]) : 1;

if (!range) {
  console.error("Usage: range-expand <range> [step]");
  console.error("Examples: range-expand 1-10 | range-expand a-z | range-expand 10-1 | range-expand 1-9,20-25");
  process.exit(1);
}

try {
  console.log(expandRange(range, { step }).join(" "));
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
