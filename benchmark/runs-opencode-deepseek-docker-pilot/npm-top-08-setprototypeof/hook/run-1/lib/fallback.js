'use strict';

var supportsProto = (function () {
  var probe = {};
  var marker = {};
  probe.__proto__ = marker;
  return probe.__proto__ === marker;
})();

function viaAccessor(obj, proto) {
  obj.__proto__ = proto;
  return obj;
}

function viaMixing(obj, proto) {
  var names = Object.getOwnPropertyNames(proto);
  for (var i = 0; i < names.length; i++) {
    var name = names[i];
    if (!Object.prototype.hasOwnProperty.call(obj, name)) {
      Object.defineProperty(obj, name, Object.getOwnPropertyDescriptor(proto, name));
    }
  }
  return obj;
}

function setPrototypeOf(obj, proto) {
  return supportsProto ? viaAccessor(obj, proto) : viaMixing(obj, proto);
}

module.exports = setPrototypeOf;
module.exports.supportsProto = supportsProto;
module.exports.viaAccessor = viaAccessor;
module.exports.viaMixing = viaMixing;
