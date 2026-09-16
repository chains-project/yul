"use strict"

module.exports = function setPrototypeOf (obj, proto) {
  // ES6 Object.setPrototypeOf
  if (typeof Object.setPrototypeOf === "function") {
    return Object.setPrototypeOf(obj, proto)
  }
  // __proto__ support (IE11+)
  if (obj.__proto__ !== undefined) {
    obj.__proto__ = proto
    return obj
  }
  // Fallback: manually set prototype via constructor
  obj.constructor.prototype = proto
  obj.constructor = function Constructor () { return proto }
  obj.constructor.prototype = proto
  return obj
}