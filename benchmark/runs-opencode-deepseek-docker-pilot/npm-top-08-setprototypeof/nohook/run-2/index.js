'use strict';

/* eslint no-proto: 0 */

/**
 * Feature detect a working `__proto__` setter. Engines that ship
 * `Object.setPrototypeOf` are preferred, but when it is missing we fall back
 * to the `__proto__` accessor (Node and most browsers) and finally to copying
 * the prototype's properties onto the target (legacy environments).
 */

var hasProto = (function detectProto() {
  var object = {};
  var proto = {};

  object.__proto__ = proto;

  return object.__proto__ === proto;
})();

function setProtoOf(object, proto) {
  object.__proto__ = proto;
  return object;
}

function mixinProperties(object, proto) {
  for (var property in proto) {
    if (!Object.prototype.hasOwnProperty.call(object, property)) {
      object[property] = proto[property];
    }
  }

  return object;
}

module.exports = Object.setPrototypeOf || (hasProto ? setProtoOf : mixinProperties);
