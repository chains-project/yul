#!/usr/bin/env node
import process from 'node:process';
import { canonicalPath } from './index.js';

const target = process.argv[2];

if (!target) {
  console.error('Usage: canonical-path <path>');
  process.exit(1);
}

try {
  process.stdout.write(`${canonicalPath(target)}\n`);
} catch (error) {
  console.error(`canonical-path: ${error.message}`);
  process.exit(1);
}
