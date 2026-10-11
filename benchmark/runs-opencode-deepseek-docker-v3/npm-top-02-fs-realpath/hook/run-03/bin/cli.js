#!/usr/bin/env node
'use strict';

var realpath = require('..');

var target = process.argv[2];

if (!target) {
  process.stderr.write('Usage: resolve-realpath <path>\n');
  process.exit(1);
}

realpath.promises(target).then(
  function (resolved) {
    process.stdout.write(resolved + '\n');
  },
  function (err) {
    process.stderr.write(err.message + '\n');
    process.exit(1);
  }
);
