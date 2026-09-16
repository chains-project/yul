/**
 * Cross-platform way to set the prototype of an object at runtime.
 *
 * Tries Object.setPrototypeOf (ES6) first, then falls back to __proto__.
 *
 * @param {Object} obj - The object to set the prototype on
 * @param {Object} proto - The new prototype
 * @returns {Object} The object with the updated prototype
 */
module.exports = function setPrototypeOf(obj, proto) {
  if (obj == null) {
    throw new TypeError('Cannot set prototype on null or undefined');
  }

  if (typeof Object.setPrototypeOf === 'function') {
    return Object.setPrototypeOf(obj, proto);
  }

  if (typeof obj.__defineGetter__ === 'function' &&
      typeof Object.getPrototypeOf === 'function') {
    // Check if __proto__ is a prototype accessor (most environments)
    const protoObj = Object.getPrototypeOf(obj);
    const hasProto = protoObj !== null && obj.__proto__ === protoObj;
    if (hasProto || (obj.__proto__ !== undefined && Object.getPrototypeOf(obj.__proto__) === null)) {
      obj.__proto__ = proto;
      return obj;
    }
  }

  if ('__proto__' in obj) {
    obj.__proto__ = proto;
    return obj;
  }

  throw new TypeError('Cannot set prototype: neither Object.setPrototypeOf nor __proto__ is available');
};

module.exports.shim = function shim() {
  if (typeof Object.setPrototypeOf !== 'function') {
    if ('__proto__' in {}) {
      // Store original __proto__ accessor
      const originalProto = Object.getOwnPropertyDescriptor(Object.prototype, '__proto__');
      Object.defineProperty(Object.prototype, '__proto__', {
        configurable: true,
        set: function(proto) {
          const self = this;
          if (self === Object.prototype || self === null) {
            return;
          }
          Object.setPrototypeOf(self, proto);
        },
        get: function() {
          const self = this;
          if (self === Object.prototype || self === null) {
            return null;
          }
          return Object.getPrototypeOf(self);
        }
      });
    }
  }
};