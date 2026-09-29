'use strict';

var fs = require('fs');
var path = require('path');

// `fs.realpathSync.native` / `fs.realpath.native` were added in Node.js 9.2.0.
// When available they delegate to realpath(3)/GetFinalPathNameByHandle, which
// canonicalizes more aggressively than the JavaScript fallback (Windows
// junctions, 8.3 short names, macOS /var -> /private/var, ...). The JavaScript
// implementation is still used on older runtimes and as a safety net if the
// native call rejects a path the JS implementation accepts.
var nativeRealpathSync =
  typeof fs.realpathSync === 'function' &&
  typeof fs.realpathSync.native === 'function'
    ? fs.realpathSync.native
    : null;

var nativeRealpath =
  typeof fs.realpath === 'function' &&
  typeof fs.realpath.native === 'function'
    ? fs.realpath.native
    : null;

function toAbsolute(target) {
  if (typeof target !== 'string') {
    throw new TypeError('The "path" argument must be of type string');
  }
  if (target.length === 0) {
    throw new TypeError('The "path" argument must not be empty');
  }
  // Resolve first so relative inputs and trailing separators behave the same on
  // every Node version, then let realpath collapse the symlinks.
  return path.resolve(target);
}

function canonicalPathSync(target, options) {
  var absolute = toAbsolute(target);
  var cache = options && options.cache;

  if (nativeRealpathSync) {
    try {
      return nativeRealpathSync(absolute, cache ? { cache: cache } : undefined);
    } catch (err) {
      if (err && err.code !== 'ENOSYS' && err.code !== 'EINVAL') {
        throw err;
      }
    }
  }
  return fs.realpathSync(absolute, cache ? { cache: cache } : undefined);
}

function canonicalPath(target, options, callback) {
  if (typeof options === 'function') {
    callback = options;
    options = undefined;
  }
  if (typeof callback !== 'function') {
    throw new TypeError('The "callback" argument must be of type function');
  }

  var absolute;
  try {
    absolute = toAbsolute(target);
  } catch (err) {
    return process.nextTick(callback, err);
  }

  var cache = options && options.cache;
  var opts = cache ? { cache: cache } : undefined;

  if (nativeRealpath) {
    nativeRealpath(absolute, opts, function (err, resolved) {
      if (!err || (err.code !== 'ENOSYS' && err.code !== 'EINVAL')) {
        return callback(err, resolved);
      }
      fs.realpath(absolute, opts, callback);
    });
    return;
  }
  fs.realpath(absolute, opts, callback);
}

module.exports = canonicalPath;
module.exports.canonicalPath = canonicalPath;
module.exports.canonicalPathSync = canonicalPathSync;
module.exports.sync = canonicalPathSync;
