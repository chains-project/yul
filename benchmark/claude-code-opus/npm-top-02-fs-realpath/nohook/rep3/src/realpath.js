'use strict';

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');

// Node ships two realpath implementations:
//   - fs.realpath / fs.realpathSync: pure JS, walks each path component with lstat/readlink.
//   - fs.realpath.native / fs.realpathSync.native / fs.promises.realpath: libuv's realpath(3).
// The native one has differed across Node versions and platforms (Windows subst/mapped
// drives, pipes and sockets, drive-letter casing, error codes). Both the sync and async
// APIs here use the JS implementation so results are identical regardless of which is
// called and stable across Node versions. Note fs.promises.realpath is NOT used: it is
// backed by the native implementation.
const realpathAsync = promisify(fs.realpath);

function normalizeInput(p) {
  if (typeof p !== 'string' && !Buffer.isBuffer(p) && !(p instanceof URL)) {
    throw new TypeError(`path must be a string, Buffer, or URL; received ${typeof p}`);
  }
  if (typeof p === 'string') {
    if (p.length === 0) throw new TypeError('path must not be empty');
    return path.resolve(p);
  }
  return p;
}

function resolveRealpathSync(p) {
  return fs.realpathSync(normalizeInput(p));
}

async function resolveRealpath(p) {
  return realpathAsync(normalizeInput(p));
}

module.exports = { resolveRealpath, resolveRealpathSync };
