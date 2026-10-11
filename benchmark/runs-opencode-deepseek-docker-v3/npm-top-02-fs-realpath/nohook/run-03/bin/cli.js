#!/usr/bin/env node
import { resolveRealPath } from "../src/index.js";

const paths = process.argv.slice(2);

if (paths.length === 0) {
  console.error("Usage: resolve-real-path <path> [path...]");
  process.exit(1);
}

let failed = false;

for (const inputPath of paths) {
  try {
    const resolved = await resolveRealPath(inputPath);
    console.log(resolved);
  } catch (error) {
    failed = true;
    console.error(`${inputPath}: ${error.message}`);
  }
}

process.exit(failed ? 1 : 0);
