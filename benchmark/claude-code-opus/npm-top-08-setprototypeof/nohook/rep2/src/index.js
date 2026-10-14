'use strict';

/**
 * Set the prototype of `obj` to `proto` and return `obj`.
 *
 * Uses the standard `Object.setPrototypeOf` (ES2015), which is available in
 * every supported Node.js version and all modern browsers, so no polyfill or
 * third-party dependency is needed.
 *
 * @template T
 * @param {T} obj
 * @param {object | null} proto
 * @returns {T}
 */
function setPrototypeOf(obj, proto) {
  return Object.setPrototypeOf(obj, proto);
}

module.exports = setPrototypeOf;
module.exports.setPrototypeOf = setPrototypeOf;
