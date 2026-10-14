'use strict';

/**
 * Set the prototype of `obj` to `proto` and return `obj`.
 *
 * Resolution order:
 *   1. Native Object.setPrototypeOf (ES2015+, all modern runtimes).
 *   2. The `__proto__` setter (legacy engines that support it).
 *   3. Copy own properties from `proto` onto `obj` (last resort; `obj` will
 *      not observe later changes to `proto`, and `instanceof` won't work).
 */
var setPrototypeOf = Object.setPrototypeOf ||
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
