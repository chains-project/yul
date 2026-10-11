'use strict';

const fs = require('fs');

function realpathSync(target) {
  if (typeof target !== 'string') {
    throw new TypeError('Expected a string path');
  }

  if (typeof fs.realpathSync.native === 'function') {
    try {
      return fs.realpathSync.native(target);
    } catch (err) {
      if (err.code !== 'ERR_FEATURE_UNAVAILABLE_ON_PLATFORM') {
        throw err;
      }
    }
  }

  return fs.realpathSync(target);
}

function realpath(target, callback) {
  if (typeof target !== 'string') {
    throw new TypeError('Expected a string path');
  }
  if (typeof callback !== 'function') {
    throw new TypeError('Expected a callback function');
  }

  const native = fs.realpath.native;
  if (typeof native === 'function') {
    native(target, function (err, resolved) {
      if (err && err.code === 'ERR_FEATURE_UNAVAILABLE_ON_PLATFORM') {
        fs.realpath(target, callback);
        return;
      }
      callback(err, resolved);
    });
    return;
  }

  fs.realpath(target, callback);
}

module.exports = realpath;
module.exports.sync = realpathSync;
module.exports.realpath = realpath;
module.exports.realpathSync = realpathSync;
module.exports.default = realpath;
