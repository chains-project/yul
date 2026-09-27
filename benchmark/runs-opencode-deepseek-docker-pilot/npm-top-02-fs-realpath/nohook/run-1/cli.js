#!/usr/bin/env node
'use strict';

const { realpath } = require('./index');

const target = process.argv[2];

if (!target) {
  console.error('usage: realpath <path>');
  process.exit(1);
}

realpath(target)
  .then((resolved) => {
    process.stdout.write(resolved + '\n');
  })
  .catch((err) => {
    console.error(err.message);
    process.exit(1);
  });
