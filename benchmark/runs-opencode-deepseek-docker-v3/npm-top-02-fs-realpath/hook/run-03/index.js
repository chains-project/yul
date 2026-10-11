'use strict';

var fs = require('fs');

var hasNativeSync = typeof fs.realpathSync.native === 'function';
var hasNativeAsync = typeof fs.realpath.native === 'function';

function realpathSync(p) {
  if (hasNativeSync) {
    return fs.realpathSync.native(p);
  }
  return fs.realpathSync(p);
}

function realpath(p, callback) {
  var fn = hasNativeAsync ? fs.realpath.native : fs.realpath;
  return fn(p, callback);
}

function realpathPromise(p) {
  return new Promise(function (resolve, reject) {
    realpath(p, function (err, resolved) {
      if (err) {
        reject(err);
      } else {
        resolve(resolved);
      }
    });
  });
}

module.exports = realpath;
module.exports.realpath = realpath;
module.exports.realpathSync = realpathSync;
module.exports.sync = realpathSync;
module.exports.promises = realpathPromise;
module.exports.hasNativeSync = hasNativeSync;
module.exports.hasNativeAsync = hasNativeAsync;
