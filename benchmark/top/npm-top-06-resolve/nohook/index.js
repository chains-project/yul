'use strict';

const resolve = require('resolve');

const EXTENSIONS = ['.js', '.json', '.node', '.mjs', '.cjs'];

function resolveModule(specifier, basedir) {
  return resolve.sync(specifier, { basedir, extensions: EXTENSIONS });
}

function resolveModuleAsync(specifier, basedir) {
  return new Promise((res, rej) => {
    resolve(specifier, { basedir, extensions: EXTENSIONS }, (err, resolved) =>
      err ? rej(err) : res(resolved)
    );
  });
}

module.exports = { resolveModule, resolveModuleAsync };
