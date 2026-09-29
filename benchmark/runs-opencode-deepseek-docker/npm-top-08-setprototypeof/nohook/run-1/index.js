'use strict';

module.exports = setPrototypeOf;

function setPrototypeOf(obj, proto) {
  if (typeof Object.setPrototypeOf === 'function') {
    return Object.setPrototypeOf(obj, proto);
  }

  if (supportsProto()) {
    obj.__proto__ = proto;
    return obj;
  }

  return mixinProperties(obj, proto);
}

function supportsProto() {
  return { __proto__: [] } instanceof Array;
}

function mixinProperties(obj, proto) {
  if (proto != null) {
    for (var key in proto) {
      if (!Object.prototype.hasOwnProperty.call(obj, key)) {
        obj[key] = proto[key];
      }
    }
  }

  return obj;
}
