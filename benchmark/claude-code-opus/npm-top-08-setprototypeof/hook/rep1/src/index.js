'use strict';

/**
 * Set the prototype of `obj` to `proto` and return `obj`.
 *
 * Uses the standard Object.setPrototypeOf when available, falling back to
 * the legacy `__proto__` setter, and finally to copying properties for
 * engines that support neither.
 *
 * @template T
 * @param {T} obj
 * @param {object | null} proto
 * @returns {T}
 */
const impl =
  typeof Object.setPrototypeOf === 'function'
    ? Object.setPrototypeOf
    : { __proto__: [] } instanceof Array
      ? setProtoOf
      : mixinProperties;

// Wrap rather than re-export so the named export below never mutates the
// built-in Object.setPrototypeOf.
function setPrototypeOf(obj, proto) {
  return impl(obj, proto);
}

function setProtoOf(obj, proto) {
  obj.__proto__ = proto;
  return obj;
}

function mixinProperties(obj, proto) {
  for (const prop in proto) {
    if (!Object.prototype.hasOwnProperty.call(obj, prop)) {
      obj[prop] = proto[prop];
    }
  }
  return obj;
}

module.exports = setPrototypeOf;
module.exports.setPrototypeOf = setPrototypeOf;
