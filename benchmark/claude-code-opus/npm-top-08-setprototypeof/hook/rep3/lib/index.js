'use strict'

/**
 * Set the prototype of `obj` to `proto` and return `obj`.
 *
 * Uses the native `Object.setPrototypeOf` when available, falls back to the
 * `__proto__` accessor, and as a last resort copies the prototype's
 * properties onto the object (for environments with neither).
 */
module.exports = Object.setPrototypeOf ||
  ({ __proto__: [] } instanceof Array ? setProtoOf : mixinProperties)

function setProtoOf (obj, proto) {
  obj.__proto__ = proto
  return obj
}

function mixinProperties (obj, proto) {
  for (const prop in proto) {
    if (!Object.prototype.hasOwnProperty.call(obj, prop)) {
      obj[prop] = proto[prop]
    }
  }
  return obj
}

module.exports.setProtoOf = setProtoOf
module.exports.mixinProperties = mixinProperties
