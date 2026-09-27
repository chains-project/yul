'use strict';

var fallback = require('./lib/fallback');

var nativeSetPrototypeOf =
  typeof Object.setPrototypeOf === 'function' ? Object.setPrototypeOf : null;

function setPrototypeOf(obj, proto) {
  if (nativeSetPrototypeOf) {
    return nativeSetPrototypeOf.call(Object, obj, proto);
  }
  return fallback(obj, proto);
}

module.exports = setPrototypeOf;
