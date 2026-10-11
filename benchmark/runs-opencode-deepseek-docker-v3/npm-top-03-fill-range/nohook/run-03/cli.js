#!/usr/bin/env node
import { expandRange } from "./index.js";

const input = process.argv[2];

if (!input) {
  console.error("Usage: expand-range <range>  (e.g. \"1-10\" or \"a-z\")");
  process.exit(1);
}

try {
  console.log(JSON.stringify(expandRange(input)));
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
