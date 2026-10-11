#!/usr/bin/env node
import { expandRange } from "../src/expand-range.js";

const input = process.argv[2];

if (input === undefined) {
  console.error("Usage: expand-range <range>  e.g. expand-range 1-10");
  process.exit(1);
}

try {
  console.log(JSON.stringify(expandRange(input)));
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
