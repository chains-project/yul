'use strict';

var setPrototypeOf = require('./');

if (typeof Object.setPrototypeOf !== 'function') {
	Object.setPrototypeOf = setPrototypeOf;
}

if (typeof Reflect === 'object' && Reflect !== null && typeof Reflect.setPrototypeOf !== 'function') {
	Reflect.setPrototypeOf = function setPrototypeOfPolyfill(target, proto) {
		if (typeof target !== 'object' && typeof target !== 'function') {
			throw new TypeError('Reflect.setPrototypeOf called on non-object');
		}
		if (proto !== null && typeof proto !== 'object' && typeof proto !== 'function') {
			throw new TypeError('Object prototype may only be an Object or null');
		}
		return setPrototypeOf(target, proto) === target;
	};
}

module.exports = setPrototypeOf;
