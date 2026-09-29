'use strict';

var hasNativeSetPrototypeOf = typeof Object.setPrototypeOf === 'function';

function typeName(value) {
  if (value === null) {
    return 'null';
  }
  if (value === undefined) {
    return 'undefined';
  }
  return typeof value + ' (' + Object.prototype.toString.call(value) + ')';
}

function isObject(value) {
  return value !== null && (typeof value === 'object' || typeof value === 'function');
}

function supportsProtoAssignment() {
  if (!('__proto__' in {})) {
    return false;
  }
  var target = {};
  var proto = {};
  try {
    target.__proto__ = proto;
  } catch (error) {
    return false;
  }
  return Object.getPrototypeOf(target) === proto;
}

function applyNative(obj, proto) {
  return Object.setPrototypeOf(obj, proto);
}

function applyProtoAssignment(obj, proto) {
  obj.__proto__ = proto;
  return obj;
}

function applyCopy(obj, proto) {
  var target = Object.create(proto);
  var names = Object.getOwnPropertyNames(obj);
  var i;
  for (i = 0; i < names.length; i++) {
    Object.defineProperty(target, names[i], Object.getOwnPropertyDescriptor(obj, names[i]));
  }
  var symbols = typeof Object.getOwnPropertySymbols === 'function' ? Object.getOwnPropertySymbols(obj) : [];
  for (i = 0; i < symbols.length; i++) {
    Object.defineProperty(target, symbols[i], Object.getOwnPropertyDescriptor(obj, symbols[i]));
  }
  return target;
}

var apply;
if (hasNativeSetPrototypeOf) {
  apply = applyNative;
} else if (supportsProtoAssignment()) {
  apply = applyProtoAssignment;
} else {
  apply = applyCopy;
}

function setPrototypeOf(obj, proto) {
  if (obj === null || obj === undefined) {
    throw new TypeError('setPrototypeOf: cannot set the prototype of ' + typeName(obj));
  }
  if (proto !== null && !isObject(proto)) {
    throw new TypeError('setPrototypeOf: the prototype must be an object or null, got ' + typeName(proto));
  }
  if (!isObject(obj)) {
    return obj;
  }
  return apply(obj, proto);
}

setPrototypeOf.strategy = hasNativeSetPrototypeOf
  ? 'native'
  : (apply === applyProtoAssignment ? '__proto__' : 'copy');

module.exports = setPrototypeOf;
