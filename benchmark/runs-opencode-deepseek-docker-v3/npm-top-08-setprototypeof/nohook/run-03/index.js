'use strict';

/**
 * Fallback for engines that expose a working `__proto__` setter.
 */
function setProtoOf(obj, proto) {
	obj.__proto__ = proto;
	return obj;
}

/**
 * Last-resort fallback: copy inherited enumerable properties onto the object.
 *
 * This cannot truly change the prototype chain, so it only approximates the
 * behavior by mixing the target prototype's properties into the object.
 */
function mixinProperties(obj, proto) {
	for (var prop in proto) {
		if (!Object.prototype.hasOwnProperty.call(obj, prop)) {
			obj[prop] = proto[prop];
		}
	}
	return obj;
}

/**
 * Picks the best available implementation for the current runtime.
 *
 * Preference order:
 *   1. Native `Object.setPrototypeOf`
 *   2. The `__proto__` setter
 *   3. Property mixin
 */
function createSetPrototypeOf() {
	if (typeof Object.setPrototypeOf === 'function') {
		return Object.setPrototypeOf;
	}

	var canUseProto = false;
	try {
		canUseProto = { __proto__: [] } instanceof Array;
	} catch (e) {
		canUseProto = false;
	}

	return canUseProto ? setProtoOf : mixinProperties;
}

var setPrototypeOf = createSetPrototypeOf();

module.exports = setPrototypeOf;
module.exports.setProtoOf = setProtoOf;
module.exports.mixinProperties = mixinProperties;
module.exports.createSetPrototypeOf = createSetPrototypeOf;
