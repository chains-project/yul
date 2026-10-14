'use strict';

/**
 * Set the prototype of `obj` to `proto` and return `obj`.
 *
 * Uses the native Object.setPrototypeOf where available (all ES2015+ engines),
 * falls back to the __proto__ setter, and finally to copying properties for
 * legacy engines that support neither.
 */
var setPrototypeOf =
  Object.setPrototypeOf ||
  ({ __proto__: [] } instanceof Array ? setProtoOf : mixinProperties);

function setProtoOf(obj, proto) {
  obj.__proto__ = proto;
  return obj;
}

function mixinProperties(obj, proto) {
  for (var prop in proto) {
    if (!Object.prototype.hasOwnProperty.call(obj, prop)) {
      obj[prop] = proto[prop];
    }
  }
  return obj;
}

module.exports = setPrototypeOf;
module.exports.setProtoOf = setProtoOf;
module.exports.mixinProperties = mixinProperties;
