'use strict';

var nativeSetPrototypeOf = Object.setPrototypeOf;

function assertObject(value, name) {
  var type = typeof value;
  if (value === null || (type !== 'object' && type !== 'function')) {
    throw new TypeError(name + ' must be an object or a function');
  }
}

function assertPrototype(proto) {
  var type = typeof proto;
  if (proto !== null && type !== 'object' && type !== 'function') {
    throw new TypeError('prototype must be an object or null');
  }
}

function setViaNative(obj, proto) {
  nativeSetPrototypeOf(obj, proto);
  return obj;
}

function setViaProto(obj, proto) {
  obj.__proto__ = proto;
  return obj;
}

function setViaCopy(obj, proto) {
  var result = Object.create(proto);
  Object.getOwnPropertyNames(obj).forEach(function (key) {
    Object.defineProperty(result, key, Object.getOwnPropertyDescriptor(obj, key));
  });
  return result;
}

var supportsProto = (function () {
  if (!('__proto__' in {})) {
    return false;
  }
  try {
    var probe = {};
    probe.__proto__ = { marker: true };
    return probe.marker === true;
  } catch (err) {
    return false;
  }
})();

var implementation;

if (nativeSetPrototypeOf) {
  implementation = setViaNative;
} else if (supportsProto) {
  implementation = setViaProto;
} else {
  implementation = setViaCopy;
}

function setPrototypeOf(obj, proto) {
  assertObject(obj, 'obj');
  assertPrototype(proto);
  return implementation(obj, proto);
}

module.exports = setPrototypeOf;
module.exports.setPrototypeOf = setPrototypeOf;
